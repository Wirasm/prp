// prp-companion live layer. Pasted verbatim, only into a review page in live mode (templates/live.md).
// In helm it shows each finding's status and one-line replies from <stem>.data.json beside the page,
// and writes the operator's changes back through helmCanvasData. Anywhere else it does nothing, and
// the page is the static companion.
(() => {
  const helm = window.webkit?.messageHandlers?.helmCanvasData;
  if (!helm) return;
  const LIVE = decodeURIComponent(location.pathname.split("/").pop()).replace(/\.html?$/i, ".data.json");
  const STATUSES = [["open", "Open"], ["fixed", "Fixed"], ["wontfix", "Won't fix"], ["question", "Question"]];
  let base = null, data = { findings: {} }, said = "read";

  const style = document.createElement("style");
  style.textContent = `
    .live { margin-top: .6rem; border-top: 1px solid var(--border); padding-top: .5rem; }
    .live .row { display: flex; flex-wrap: wrap; gap: .4rem; align-items: center; }
    .live button { font: inherit; font-size: 13px; color: var(--muted); background: var(--surface);
      border: 1px solid var(--border); border-radius: 4px; padding: .1rem .5rem; cursor: pointer; }
    .live button.on { color: var(--surface); background: var(--accent); border-color: var(--accent); }
    .live input { flex: 1 1 14rem; font: inherit; font-size: 13px; color: var(--text); background: var(--surface);
      border: 1px solid var(--border); border-radius: 4px; padding: .15rem .45rem; }
    .live p { margin: .35rem 0 0; font-size: 14px; }
    .live .who { color: var(--faint); font-size: 12px; text-transform: uppercase; margin-right: .4rem; }
    [data-live="fixed"], [data-live="wontfix"] { opacity: .65; }
    [data-live="question"] { border-color: var(--attention); }
    #live-line { color: var(--muted); font-size: 13px; }`;
  document.head.appendChild(style);

  // The card's controls, built once; render() keeps them current.
  function controls(id) {
    const live = document.createElement("div");
    live.className = "live";
    const row = document.createElement("div");
    row.className = "row";
    for (const [s, label] of STATUSES) {
      const b = document.createElement("button");
      b.dataset.s = s;
      b.textContent = label;
      b.onclick = () => change((d) => { d.findings[id].status = s; });
      row.append(b);
    }
    const input = document.createElement("input");
    input.className = "reply";
    input.placeholder = "One line to the reviewer, Enter to send";
    input.onkeydown = (e) => {
      const v = input.value.trim();
      if (e.key !== "Enter" || !v) return;
      input.value = "";
      change((d) => { d.findings[id].reply = v; });
    };
    row.append(input);
    const op = document.createElement("p"), agent = document.createElement("p");
    op.className = "op";
    agent.className = "agent";
    live.append(row, op, agent);
    return live;
  }

  function say(el, who, text) {
    el.textContent = "";
    if (!text) return;
    const w = document.createElement("span");
    w.className = "who";
    w.textContent = who;
    el.append(w, text);
  }

  function render() {
    const counts = {};
    for (const [id, item] of Object.entries(data.findings || {})) {
      const card = document.getElementById(id);
      if (!card) continue;
      counts[item.status] = (counts[item.status] || 0) + 1;
      let live = card.querySelector(":scope > .live");
      if (!live) card.append(live = controls(id));
      live.querySelectorAll("button").forEach((b) => b.classList.toggle("on", b.dataset.s === item.status));
      say(live.querySelector(".op"), "you", item.reply);
      say(live.querySelector(".agent"), "reviewer", item.note);
      card.dataset.live = item.status;
    }
    const line = document.getElementById("live-line");
    if (line) {
      const tally = STATUSES.filter(([s]) => counts[s]).map(([s, l]) => `${counts[s]} ${l.toLowerCase()}`);
      line.textContent = [...tally, `${said} ${new Date().toLocaleTimeString()}`].join(" · ");
    }
  }

  async function load() {
    const res = await fetch(`./${encodeURIComponent(LIVE)}`, { cache: "no-store" }).catch(() => null);
    base = res && res.ok ? await res.text() : null;
    data = base ? JSON.parse(base) : { findings: {} };
    data.findings ||= {};
    said = "read";
    render();
  }

  // A change is a function of the data, so it can be applied again to a newer version.
  async function change(edit) {
    try {
      edit(data);
      render();
      const answer = await helm.postMessage({ kind: "canvas.data.write", data, base });
      base = answer.text;
      if (answer.kind === "changed") { data = JSON.parse(answer.text); return await change(edit); }
      said = "saved";
    } catch (e) {
      said = `not saved (${e})`;
    }
    render();
  }

  // helm tells the page its data file changed. A change to the page itself is left to the operator.
  window.helmCanvasUpdate = (update) => {
    if (update && update.file === LIVE) { load(); return true; }
    return false;
  };

  load();
})();
