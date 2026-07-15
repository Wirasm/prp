# Multi-Agent Review Summary Format

**MANDATORY**: When running the `--agents` (multi-agent) mode, aggregate every agent's findings into exactly this format. Do not improvise a different shape — downstream tooling (e.g. `prp-loop`) reads this structure.

## Categories

| Category | Description | Action |
|----------|-------------|--------|
| **Critical** | Must fix before merge | Block merge |
| **Important** | Should fix | Address before merge |
| **Suggestions** | Nice to have | Consider |
| **Strengths** | What's good | Acknowledge |

## Summary Format

```markdown
## PR Review Summary

### Critical Issues (X found)
| Agent | Issue | Location |
|-------|-------|----------|
| code-reviewer | Description | `file.ts:line` |

### Important Issues (X found)
| Agent | Issue | Location |
|-------|-------|----------|
| silent-failure-hunter | Description | `file.ts:line` |

### Suggestions (X found)
| Agent | Suggestion | Location |
|-------|------------|----------|
| type-design-analyzer | Description | `file.ts:line` |

### Strengths
- Well-structured error handling
- Good test coverage for critical paths

### Documentation Issues
- `CLAUDE.md` - Stale command reference needs update
- `README.md` - Configuration section outdated

### Verdict
[READY TO MERGE / NEEDS FIXES / CRITICAL ISSUES]

### Recommended Actions
1. Fix critical issues first
2. Address important issues
3. Consider suggestions
4. Re-run review after fixes
```
