# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
prp_loop.py — autonomous, cyclic PRP pipeline orchestrator.

Pipeline:
    plan -> implement (loop until green, commit, open PR) -> review
    review clean? -> done
    review dirty? -> fix (loop until green) -> push -> review   (cyclic, bounded)

Design:
- Headless: each stage is one CLI call in a fresh session — `claude -p "<prompt>"` by
  default, or `codex exec "<prompt>"` with --cli codex (the CLI choice persists in state).
- State lives in ~/.prp/<key>/state/prp-loop.state.json (resumable: re-run with --resume).
- Fully autonomous (permission/sandbox bypass flags per CLI).
- Self-contained: this script owns both loops itself and detects "green" from each
  stage's `VALIDATION: GREEN` sentinel (parsed from the clean result text) and/or an
  optional hard `--validate` command (authoritative). No external Stop-hook involved.
- Stages are invoked by naming the skill in a natural-language prompt, so the
  agent-invocable PRP skills auto-load. Skills are never modified.
- Bounded by --max-cycles (outer review loop) and --max-implement-iterations (inner).
- --until <stage> stops after the named stage completes. `--until implement` stops
  after the implementation is green, committed, and opened as a PR.

Usage:
    uv run .claude/skills/prp-loop/scripts/prp_loop.py "implement feature X" [--base main]
    uv run .claude/skills/prp-loop/scripts/prp_loop.py "implement feature X" --until implement  # green + PR, no review
    uv run .claude/skills/prp-loop/scripts/prp_loop.py --resume
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

def _project_root() -> Path:
    """The project being operated on — the user's repo, NOT where this script lives.
    Location-agnostic: derive the root from git (else cwd), so the identical script
    works whether it sits in a local skill or is bundled inside a plugin skill."""
    try:
        top = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True
        ).stdout.strip()
        if top:
            return Path(top)
    except Exception:
        pass
    return Path.cwd()


def _prp_dir() -> Path:
    """Resolve the per-project PRP store shared by the main checkout and worktrees."""
    common = subprocess.run(
        ["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
        capture_output=True,
        text=True,
    )
    gd = common.stdout.strip() if common.returncode == 0 else ""
    if gd.endswith("/.git"):
        root = Path(gd[:-5]).resolve()
    elif gd:
        root = Path(gd).resolve()
    else:
        root = Path.cwd().resolve()

    name = re.sub(r"[^a-z0-9]+", "-", root.name.lower()).strip("-") or "project"
    hashed = subprocess.run(
        ["git", "hash-object", "--stdin"],
        input=str(root),
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()[:8]
    prp_dir = Path(os.environ.get("PRP_HOME", Path.home() / ".prp")) / f"{name}-{hashed}"
    prp_dir.mkdir(parents=True, exist_ok=True)
    registration = prp_dir / "project.json"
    if registration.exists():
        try:
            registered_path = json.loads(registration.read_text()).get("path")
        except (json.JSONDecodeError, OSError) as exc:
            sys.exit(f"invalid PRP project registration at {registration}: {exc}")
        if registered_path != str(root):
            sys.exit(
                f"PRP project-key collision: {registration} belongs to {registered_path!r}, "
                f"not {str(root)!r}"
            )
    else:
        registration.write_text(json.dumps({"path": str(root), "name": name}) + "\n")
    return prp_dir


ROOT = _project_root()  # worktree being operated on (git toplevel, else cwd)
PRP_DIR = _prp_dir()  # store shared by all worktrees of the main checkout
STATE_FILE = PRP_DIR / "state" / "prp-loop.state.json"
PLANS_DIR = PRP_DIR / "plans"
REVIEW_DIR = PRP_DIR / "reviews"
LEGACY_STATE_FILE = ROOT / ".claude" / "prp-loop.state.json"

GREEN = "VALIDATION: GREEN"
PROTECTED_BRANCHES = {"main", "master", "development", "develop"}
STAGE_TIMEOUT = 3600  # seconds per agent stage
CLI = "claude"  # which headless CLI drives the stages; set in main(), persisted in state
# The loop's own artifacts — never commit these, even when the target repo doesn't gitignore them.
LOOP_ARTIFACTS = (
    ".claude/prp-loop.state.json*",  # state file + its atomic-write temp
    ".claude/prp-loop.run.log",
)


def log(msg: str) -> None:
    print(f"[prp-loop] {msg}", flush=True)


def now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


# ---------- state ----------
def load_state() -> dict | None:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except json.JSONDecodeError as e:
            sys.exit(f"state file {STATE_FILE} is corrupt ({e}); fix or delete it to start over")
    return None


def save_state(state: dict) -> None:
    state["updated_at"] = now()
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = STATE_FILE.with_name(STATE_FILE.name + ".tmp")
    tmp.write_text(json.dumps(state, indent=2))
    os.replace(tmp, STATE_FILE)  # atomic: a crash mid-write never corrupts the state file


def record(state: dict, stage: str, result: str) -> None:
    state.setdefault("history", []).append(
        {"stage": stage, "cycle": state["cycle"], "result": result, "at": now()}
    )


def halt(state: dict, reason: str) -> None:
    state["status"] = "halted"
    state["halt_reason"] = reason
    save_state(state)
    log(f"HALTED: {reason}")
    log(f"State preserved at {STATE_FILE}. Fix, then re-run with --resume.")
    sys.exit(1)


# ---------- shells ----------
def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=ROOT, capture_output=True, text=True
    ).stdout.strip()


def run_agent(prompt: str) -> str:
    """Run one headless agent stage via the configured CLI; return its final result text."""
    return _run_codex(prompt) if CLI == "codex" else _run_claude(prompt)


def _run_claude(prompt: str) -> str:
    cmd = [
        "claude", "-p", prompt,
        "--dangerously-skip-permissions",
        "--output-format", "json",
    ]
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=STAGE_TIMEOUT)
    if proc.returncode != 0:
        raise RuntimeError(f"claude exited {proc.returncode}: {proc.stderr[:500]}")
    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return proc.stdout  # tolerate plain text
    if data.get("is_error"):
        raise RuntimeError(f"stage reported an error: {str(data.get('result'))[:500]}")
    return str(data.get("result", ""))


def _run_codex(prompt: str) -> str:
    """`codex exec --json` emits a JSONL event stream; collect the final agent message.
    Parsing is deliberately tolerant of event-schema drift: unknown lines are skipped and
    an empty extraction falls back to the raw stream tail (check_green still gates it)."""
    cmd = [
        "codex", "exec", "--json",
        "--dangerously-bypass-approvals-and-sandbox",
        prompt,
    ]
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=STAGE_TIMEOUT)
    if proc.returncode != 0:
        raise RuntimeError(f"codex exited {proc.returncode}: {proc.stderr[:500]}")
    last_message, error = "", ""
    for line in proc.stdout.splitlines():
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        etype = str(ev.get("type", ""))
        item = ev.get("item") or {}
        if etype == "item.completed" and str(
            item.get("item_type") or item.get("type") or ""
        ) in ("agent_message", "assistant_message", "message"):
            last_message = str(item.get("text") or item.get("content") or last_message)
        elif etype in ("turn.failed", "error"):
            error = str(ev.get("error") or ev)[:500]
    if error:
        raise RuntimeError(f"codex stage reported an error: {error}")
    return last_message or proc.stdout[-2000:]


# ---------- helpers ----------
def plan_snapshot() -> dict[str, float]:
    if not PLANS_DIR.exists():
        return {}
    return {str(p): p.stat().st_mtime for p in PLANS_DIR.glob("*.plan.md")}


def newest_plan(before: dict[str, float]) -> str | None:
    """The plan written by this run's plan stage — new or modified since the snapshot,
    never a pre-existing plan that happened to be lying around."""
    if not PLANS_DIR.exists():
        return None
    fresh = [
        p for p in PLANS_DIR.glob("*.plan.md")
        if str(p) not in before or p.stat().st_mtime > before[str(p)]
    ]
    if not fresh:
        return None
    return str(max(fresh, key=lambda p: p.stat().st_mtime))


def current_pr() -> tuple[int | None, str | None]:
    out = subprocess.run(
        ["gh", "pr", "view", "--json", "number,url"],
        cwd=ROOT, capture_output=True, text=True,
    )
    if out.returncode != 0:
        return None, None
    d = json.loads(out.stdout)
    return d.get("number"), d.get("url")


def review_contract(report_path: Path) -> tuple[str | None, str | None]:
    """Read the canonical verdict and verified GitHub publication from a review report."""
    if not report_path.exists():
        return None, None
    report = report_path.read_text()
    verdict = re.search(
        r"^verdict:\s*(READY TO MERGE|NEEDS FIXES|REVIEW INCOMPLETE)\s*$", report, re.M
    )
    publication = re.search(r"^publication:\s*(https://\S+)\s*$", report, re.M)
    return (verdict.group(1) if verdict else None, publication.group(1) if publication else None)


def publication_exists(pr_number: int, publication_url: str) -> bool:
    """Verify the recorded review publication is still attached to this PR on GitHub."""
    out = subprocess.run(
        ["gh", "pr", "view", str(pr_number), "--json", "comments,reviews"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if out.returncode != 0:
        return False
    try:
        return publication_url in json.dumps(json.loads(out.stdout))
    except json.JSONDecodeError:
        return False


def _excludes() -> list[str]:
    return [f":(exclude){p}" for p in LOOP_ARTIFACTS]


def _dirty() -> str:
    """Porcelain status, excluding the loop's own artifacts so we never sweep them in."""
    return git("status", "--porcelain", "--", ".", *_excludes())


def ensure_committed(state: dict) -> None:
    """Ensure implement's changes are committed, but NEVER commit the loop's own artifacts
    (state.json / run.log) — even if the target repo doesn't gitignore them."""
    if _dirty():
        log("uncommitted changes remain; committing via prp-commit")
        run_agent("Use the prp-commit skill to commit all current changes.")
    if _dirty():
        subprocess.run(["git", "add", "-A", "--", ".", *_excludes()], cwd=ROOT)
        commit = subprocess.run(
            ["git", "commit", "-m", "chore: prp-loop checkpoint"],
            cwd=ROOT, capture_output=True, text=True,
        )
        if commit.returncode != 0 or _dirty():
            halt(state, f"checkpoint commit failed: {(commit.stderr or commit.stdout)[:300]}")


def check_green(state: dict, result: str) -> tuple[bool, str]:
    """Decide whether validations pass. --validate is authoritative if provided."""
    cmd = state.get("validate_cmd")
    if cmd:
        proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, shell=True)
        return proc.returncode == 0, (proc.stdout + proc.stderr)[-2000:]
    # The stage is told to END its message with the sentinel; require it at the end so a
    # mere echo of the instruction in the body never counts as green.
    if result.rstrip().endswith(GREEN):
        return True, ""
    if "VALIDATION: FAILED" in result:
        return False, result.split("VALIDATION: FAILED", 1)[-1][:2000]
    return False, result[-2000:]


def implement_until_green(
    state: dict, initial_prompt: str, label: str, handoff_context: str = ""
) -> bool:
    prompt = initial_prompt
    for i in range(1, state["max_implement_iterations"] + 1):
        log(f"{label} iteration {i}/{state['max_implement_iterations']} (cycle {state['cycle']})")
        result = run_agent(prompt)
        green, failures = check_green(state, result)
        if green:
            record(state, label, f"green@{i}")
            save_state(state)
            return True
        plan = state.get("artifacts", {}).get("plan_path")
        plan_ref = f" against the plan at {plan}" if plan else ""
        prompt = (
            f"Continue working on the current branch{plan_ref}. The previous attempt's "
            f"validations did not pass:\n{failures}\n\n"
            f"{handoff_context}\n\n"
            "Fix the failures, re-run ALL validations, and commit. End your message with "
            f"exactly '{GREEN}' when everything passes, otherwise 'VALIDATION: FAILED' "
            "followed by the failing output."
        )
        save_state(state)
    return False


# ---------- stages ----------
def stage_plan(state: dict) -> None:
    log("STAGE plan")
    before = plan_snapshot()
    run_agent(f"Use the prp-plan skill to create an implementation plan for: {state['feature']}")
    plan = newest_plan(before)
    if not plan:
        halt(state, f"plan stage produced no new .plan.md under {PLANS_DIR}/")
    state["artifacts"]["plan_path"] = plan
    record(state, "plan", "ok")
    state["stage"] = "implement"
    save_state(state)
    log(f"plan -> {plan}")


def stage_implement(state: dict) -> None:
    log("STAGE implement")
    plan = state["artifacts"]["plan_path"]
    base_arg = f" --base {state['base']}" if state.get("base") else ""
    initial = (
        f"Use the prp-implement skill to execute the plan at {plan}{base_arg}. "
        "Run ALL validations and commit your work. End your message with exactly "
        f"'{GREEN}' if every validation passes, otherwise end with 'VALIDATION: FAILED' "
        "followed by the failing output."
    )
    if not implement_until_green(state, initial, "implement"):
        halt(state, f"implement not green after {state['max_implement_iterations']} iterations")
    ensure_committed(state)
    num, url = current_pr()
    if num:
        state["artifacts"]["branch"] = git("rev-parse", "--abbrev-ref", "HEAD")
        state["artifacts"]["pr_number"] = num
        state["artifacts"]["pr_url"] = url
        record(state, "pr", f"#{num}")
        state["stage"] = "review"
        log(f"implement opened PR #{num} {url}")
    else:
        state["stage"] = "pr"
    save_state(state)


def stage_pr(state: dict) -> None:
    log("STAGE pr")
    branch = git("rev-parse", "--abbrev-ref", "HEAD")
    if not branch or branch in PROTECTED_BRANCHES or branch == (state.get("base") or ""):
        halt(state, f"refusing to open a PR from base/protected branch '{branch}'")
    state["artifacts"]["branch"] = branch
    base_arg = f" --base {state['base']}" if state.get("base") else ""
    plan = state["artifacts"]["plan_path"]
    run_agent(
        f"Use the prp-pr skill to push the current branch and open a pull request{base_arg}. "
        f"Read the plan at {plan} and pass its Source Issue and verified Plan Publication URL "
        "into the PR description when present."
    )
    num, url = current_pr()
    if not num:
        halt(state, "pr stage did not produce a discoverable PR (gh pr view failed)")
    state["artifacts"]["pr_number"] = num
    state["artifacts"]["pr_url"] = url
    record(state, "pr", f"#{num}")
    state["stage"] = "review"
    save_state(state)
    log(f"pr -> #{num} {url}")


def stage_review(state: dict) -> None:
    log("STAGE review")
    num = state["artifacts"]["pr_number"]
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REVIEW_DIR / f"pr-{num}-review.md"
    prompt = (
        f"Use the prp-review skill to review PR #{num}. Publish the complete canonical report "
        "to GitHub and verify its publication URL."
    )
    report_path.unlink(missing_ok=True)  # never trust a stale report from a prior attempt
    run_agent(prompt)
    if not report_path.exists():
        halt(state, f"review stage did not write the canonical report {report_path}")
    verdict, publication = review_contract(report_path)
    if not verdict:
        halt(state, f"review report has no canonical verdict: {report_path}")
    if not publication or not publication_exists(num, publication):
        halt(state, f"review report has no verified GitHub publication: {report_path}")
    state["artifacts"]["review_report"] = str(report_path)
    state["artifacts"]["review_publication"] = publication

    if verdict == "READY TO MERGE":
        record(state, "review", "clean")
        state["stage"] = "done"
        state["status"] = "done"
        save_state(state)
        log("review CLEAN — pipeline complete")
        return

    if verdict == "REVIEW INCOMPLETE":
        halt(state, f"review incomplete; inspect the published report at {report_path}")

    record(state, "review", "needs-fixes")
    if state["cycle"] >= state["max_cycles"]:
        halt(state, f"review still dirty after {state['max_cycles']} cycles; PR #{num} left open for review")
    state["cycle"] += 1
    state["stage"] = "fix"
    save_state(state)
    log(f"review needs fixes — entering cycle {state['cycle']}")


def stage_fix(state: dict) -> None:
    log("STAGE fix")
    plan = state["artifacts"]["plan_path"]
    pr_num = state["artifacts"]["pr_number"]
    review_report = state["artifacts"].get("review_report")
    if not review_report:
        legacy_report = REVIEW_DIR / f"pr-{pr_num}-review.md"
        legacy_verdict, _ = review_contract(legacy_report)
        if legacy_verdict == "NEEDS FIXES":
            review_report = str(legacy_report)
            state["artifacts"]["review_report"] = review_report
            save_state(state)
    if not review_report or not Path(review_report).exists():
        halt(state, "fix pass has no complete canonical review report")
    head_before = git("rev-parse", "HEAD")
    if not head_before:
        halt(state, "could not resolve HEAD before the fix pass")
    initial = (
        f"Use the prp-implement skill in review-correction mode for PR #{pr_num}. "
        f"Read the complete review report at {review_report} and the original plan at {plan}. "
        "Address every Critical and Important finding, preserve optional Suggestions as optional, "
        "run ALL validations, and commit. End your message with exactly "
        f"'{GREEN}' when everything passes, otherwise 'VALIDATION: FAILED' + the output."
    )
    handoff = (
        f"Continue the review correction for PR #{pr_num}. Re-read the complete review report "
        f"at {review_report} and the original plan at {plan}; do not rely on a findings summary."
    )
    if not implement_until_green(state, initial, "fix", handoff):
        halt(state, f"fix pass not green after {state['max_implement_iterations']} iterations")
    ensure_committed(state)
    if git("rev-parse", "HEAD") == head_before:
        halt(state, "fix pass produced no new commit (no progress) — halting to avoid an infinite loop")
    push = subprocess.run(["git", "push"], cwd=ROOT, capture_output=True, text=True)
    if push.returncode != 0:
        halt(state, f"git push failed: {push.stderr[:300]}")
    record(state, "fix", "pushed")
    state["stage"] = "review"
    save_state(state)


STAGES = {
    "plan": stage_plan,
    "implement": stage_implement,
    "pr": stage_pr,
    "review": stage_review,
    "fix": stage_fix,
}


def main() -> None:
    ap = argparse.ArgumentParser(description="Autonomous cyclic PRP pipeline (plan->implement+PR->review).")
    ap.add_argument("feature", nargs="?", help="Feature description, or path to a PRD/plan.")
    ap.add_argument("--base", help="Base branch (default: auto-detected by the skills).")
    ap.add_argument("--max-cycles", type=int, default=3, help="Max review->fix cycles (default 3).")
    ap.add_argument("--max-implement-iterations", type=int, default=10,
                    help="Max implement/fix iterations per stage (default 10).")
    ap.add_argument("--clean-bar", help=argparse.SUPPRESS)  # retired; canonical review verdict owns the bar
    ap.add_argument("--validate", dest="validate_cmd",
                    help="Authoritative shell command for green (exit 0 = pass). "
                         "If omitted, falls back to the VALIDATION: GREEN sentinel.")
    ap.add_argument("--until", dest="until_stage",
                    choices=["plan", "implement", "pr", "review", "fix"],
                    help="Stop after the named stage completes. '--until implement' stops after "
                         "the implementation is green, committed, and opened as a PR.")
    ap.add_argument("--resume", action="store_true", help="Resume from the existing state file.")
    ap.add_argument("--cli", choices=["claude", "codex"], default=None,
                    help="Headless CLI that drives the stages (default: claude; "
                         "a resumed loop keeps its original CLI unless overridden).")
    args = ap.parse_args()

    if not STATE_FILE.exists() and LEGACY_STATE_FILE.exists():
        sys.exit(
            f"legacy loop state found at {LEGACY_STATE_FILE}; finish it with the previous "
            f"version or move it to {STATE_FILE}"
        )

    state = load_state()
    if args.resume:
        if not state:
            sys.exit("no state file to resume from")
        state["status"] = "running"
        if args.until_stage:  # allow narrowing/overriding the stop point on resume
            state["until"] = args.until_stage
        if args.cli:
            state["cli"] = args.cli
        log(f"resuming at stage={state['stage']} cycle={state['cycle']}")
    else:
        if state and state.get("status") in ("running", "halted"):
            sys.exit(
                f"a loop with status '{state.get('status')}' exists "
                f"({STATE_FILE}); use --resume or delete it"
            )
        if not args.feature:
            sys.exit("a feature description is required to start a new loop")
        state = {
            "loop_id": f"prp-loop-{now()}",
            "feature": args.feature,
            "stage": "plan",
            "cycle": 0,
            "max_cycles": args.max_cycles,
            "max_implement_iterations": args.max_implement_iterations,
            "validate_cmd": args.validate_cmd,
            "until": args.until_stage,
            "base": args.base,
            "cli": args.cli or "claude",
            "status": "running",
            "artifacts": {},
            "history": [],
            "started_at": now(),
        }
        save_state(state)

    global CLI
    CLI = state.get("cli", "claude")

    until = state.get("until")
    while state["stage"] != "done":
        stage = state["stage"]
        try:
            STAGES[stage](state)
        except SystemExit:
            raise
        except Exception as e:  # noqa: BLE001 - top-level guard halts with preserved state
            halt(state, f"stage '{stage}' raised: {e}")
        if until and stage == until and state["stage"] != "done":
            state["status"] = "done"
            state["stage"] = "done"
            save_state(state)
            log(f"reached --until {until}; stopping after stage '{stage}' (no further stages)")
            break

    pr_url = state["artifacts"].get("pr_url")
    log(f"DONE. PR: {pr_url}" if pr_url else "DONE. (stopped before PR)")


if __name__ == "__main__":
    main()
