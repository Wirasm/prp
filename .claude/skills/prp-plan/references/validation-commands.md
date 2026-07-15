# Validation Commands — Per-Language Catalog

Concrete commands to substitute for the `{runner}` placeholders in the plan's "Validation Commands" section (see the level structure in `templates/plan-template.md`). Always replace placeholders with actual commands from the project's package.json/config — verify the script names exist before embedding them.

## Level 1: STATIC_ANALYSIS

Examples: `npm run lint`, `pnpm lint`, `ruff check . && mypy .`, `cargo clippy`

## Level 2: UNIT_TESTS

Examples: `npm test`, `pytest tests/`, `cargo test`, `go test ./...`

## Level 3: FULL_SUITE

Examples: `npm test && npm run build`, `cargo test && cargo build`

## Levels 4-6

Levels 4 (DATABASE_VALIDATION), 5 (BROWSER_VALIDATION), and 6 (MANUAL_VALIDATION) have no generic catalog — they are project-specific MCP tooling (e.g. Supabase MCP, Browser MCP) or step-by-step manual checks, as shaped in the plan template. Include them only where applicable.
