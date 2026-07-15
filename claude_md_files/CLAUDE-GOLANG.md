# CLAUDE.md

This file provides comprehensive guidance to Claude Code when working with Go (1.24+) code in this repository.

## Core Development Philosophy

### KISS (Keep It Simple, Stupid)

Simplicity should be a key goal in design. Choose straightforward solutions over complex ones whenever possible. Go was designed for simplicity — embrace it. Prefer the standard library over frameworks, and plain functions over layers of abstraction.

### YAGNI (You Aren't Gonna Need It)

Avoid building functionality on speculation. Implement features only when they are needed, not when you anticipate they might be useful in the future. Do not introduce interfaces before there is a second implementation.

### Go Proverbs (apply them)

- **Clear is better than clever** — optimize for the reader, not the writer.
- **Errors are values** — handle them explicitly; never discard them.
- **Don't communicate by sharing memory, share memory by communicating** — prefer channels for handoff of ownership.
- **A little copying is better than a little dependency** — think twice before adding a module dependency.
- **The bigger the interface, the weaker the abstraction** — keep interfaces small (1-3 methods).
- **Make the zero value useful** — design structs so `var x T` is immediately usable when possible.

## 🧱 Code Structure & Modularity

### File and Function Limits

- **Never create a file longer than 500 lines of code**. If approaching this limit, split into multiple files within the same package.
- **Functions should be under 50 lines** with a single, clear responsibility.
- **Keep cyclomatic complexity under 10** — early returns and small helpers, not nested conditionals.
- **Organize code into packages by responsibility**, not by kind (avoid `utils`, `helpers`, `common` grab-bag packages).
- **Line length should be max 120 characters** — gofmt does not enforce this, so exercise judgment.

### Project Architecture

Follow the standard Go module layout:

```
myproject/
    go.mod
    go.sum
    README.md
    Makefile

    cmd/                      # Entry points (one subdirectory per binary)
        myapp/
            main.go           # Thin main: wire dependencies, call into internal/
        myworker/
            main.go

    internal/                 # Private application code (compiler-enforced)
        server/
            server.go
            server_test.go
            routes.go
        user/
            user.go           # Domain type + business logic
            user_test.go
            repository.go     # Storage interface + implementation
            repository_test.go
        payment/
            processor.go
            processor_test.go
        config/
            config.go
            config_test.go

    testdata/                 # Test fixtures (ignored by the go tool)
```

**Rules:**

- `main.go` stays thin — parse flags/env, build dependencies, delegate to `internal/`.
- Use `internal/` for everything not meant to be imported by other modules.
- Only create a `pkg/` (or top-level exported packages) when external consumers actually exist — YAGNI.
- Test files live next to the code they test (`foo.go` → `foo_test.go`). This is the Go convention, not optional.
- Package names are short, lowercase, singular, no underscores: `user`, not `user_helpers` or `userUtils`.

## 🛠️ Development Environment

### Go Toolchain

This project uses the standard Go toolchain with modules.

```bash
# Initialize a module (once)
go mod init github.com/org/myproject

# Add a dependency (ALWAYS use go get, never edit go.mod by hand)
go get github.com/some/dependency@latest

# Add a specific version
go get github.com/some/dependency@v1.2.3

# Remove unused dependencies and verify go.sum
go mod tidy

# Track dev tools in go.mod (Go 1.24+ tool directive)
go get -tool honnef.co/go/tools/cmd/staticcheck
go tool staticcheck ./...

# Upgrade dependencies (deliberately, reviewing changelogs)
go get -u ./...
go mod tidy
```

### Development Commands

```bash
# Build everything
go build ./...

# Run the application
go run ./cmd/myapp

# Run all tests (always with the race detector locally)
go test -race ./...

# Run a specific test with verbose output
go test -race -run TestUserCanUpdateEmail ./internal/user/ -v

# Run tests with coverage
go test -race -coverprofile=coverage.out ./...
go tool cover -html=coverage.out

# Format code (gofumpt is a stricter gofmt)
gofmt -w .
gofumpt -w .        # preferred if installed

# Vet (catches real bugs — run it every time)
go vet ./...

# Lint (the standard meta-linter)
golangci-lint run

# Scan for known vulnerabilities
govulncheck ./...
```

### golangci-lint Configuration

```yaml
# .golangci.yml
version: "2"
linters:
  default: standard # govet, staticcheck, errcheck, ineffassign, unused
  enable:
    - gocritic
    - gosec
    - misspell
    - revive
    - unconvert
    - unparam
formatters:
  enable:
    - gofumpt
    - goimports
```

## 📋 Style & Conventions

### Go Style Guide

- **gofmt is law** — never argue with the formatter, never hand-format. CI must reject unformatted code.
- **Follow [Effective Go](https://go.dev/doc/effective_go) and [Go Code Review Comments](https://go.dev/wiki/CodeReviewComments)** — these are the canonical style references.
- **`goimports` manages imports** — grouped stdlib first, then third-party, then local.
- **Accept interfaces, return structs** — take the narrowest interface you need as a parameter; return concrete types.
- **`context.Context` is always the first parameter** and is never stored in a struct:

```go
func (s *Server) ProcessOrder(ctx context.Context, orderID string) (*Order, error)
```

### Naming Conventions

- **Packages**: short, lowercase, no underscores — `httputil`, not `http_util`
- **Exported identifiers**: `MixedCaps` — `UserRepository`, `MaxRetries`
- **Unexported identifiers**: `mixedCaps` — `userCache`, `defaultTimeout`
- **Interfaces**: `-er` suffix for single-method interfaces — `Reader`, `Validator`, `OrderProcessor`
- **Receivers**: one or two letters, consistent across methods — `func (s *Server)`, never `func (this *Server)` or `func (self *Server)`
- **Errors**: sentinel errors are `ErrXxx` (`ErrNotFound`); error types are `XxxError` (`ValidationError`)
- **No stutter**: `user.New()`, not `user.NewUser()`; `bytes.Buffer`, not `bytes.BytesBuffer`
- **Acronyms keep their case**: `userID`, `parseURL`, `httpClient` — never `userId` or `parseUrl`

### Doc Comments

Every exported identifier gets a doc comment that starts with its name:

```go
// UserRepository provides access to the user store.
type UserRepository interface {
	// GetByID returns the user with the given ID.
	// It returns ErrNotFound if no user exists.
	GetByID(ctx context.Context, id string) (*User, error)
}

// NewServer creates a Server with the given options.
// It returns an error if the configuration is invalid.
func NewServer(cfg Config) (*Server, error) {
```

- Complex logic should have inline comments with `// Reason:` prefix explaining the why, not the what.

## 🚨 Error Handling (THE Go Discipline)

Error handling is not boilerplate — it is the core control flow of Go programs. Treat it accordingly.

### Rules

- **NEVER ignore an error.** `_ = err` or a blank `if err != nil {}` requires a `// Reason:` comment and is almost always wrong.
- **NEVER panic in library code.** Panics are for unrecoverable programmer errors (impossible states), not for I/O or validation failures.
- **Wrap with context using `%w`** so callers can use `errors.Is` / `errors.As`:

```go
func (r *Repository) GetUser(ctx context.Context, id string) (*User, error) {
	user, err := r.queryUser(ctx, id)
	if err != nil {
		return nil, fmt.Errorf("get user %q: %w", id, err)
	}
	return user, nil
}
```

- **Error strings**: lowercase, no trailing punctuation, no "failed to" prefix chains — the wrapping provides the chain: `"open config: read /etc/app.yaml: permission denied"`.
- **Handle an error exactly once** — either log it OR return it, never both (double-logging is noise).

### Sentinel Errors and Error Types

```go
// Sentinel errors for expected conditions callers branch on.
var (
	ErrNotFound     = errors.New("not found")
	ErrUnauthorized = errors.New("unauthorized")
)

// Custom error types when callers need structured data.
type ValidationError struct {
	Field  string
	Reason string
}

func (e *ValidationError) Error() string {
	return fmt.Sprintf("validation failed on %s: %s", e.Field, e.Reason)
}

// Caller side: errors.Is for sentinels, errors.As for types.
user, err := repo.GetUser(ctx, id)
switch {
case errors.Is(err, ErrNotFound):
	return nil, status.Errorf(codes.NotFound, "user %s not found", id)
case err != nil:
	return nil, fmt.Errorf("load user: %w", err)
}

var vErr *ValidationError
if errors.As(err, &vErr) {
	log.Warn("invalid input", "field", vErr.Field)
}
```

### Resource Cleanup

```go
// Always pair acquisition with deferred release — and check close errors on writes.
f, err := os.Create(path)
if err != nil {
	return fmt.Errorf("create %s: %w", path, err)
}
defer func() {
	if cerr := f.Close(); cerr != nil && err == nil {
		err = fmt.Errorf("close %s: %w", path, cerr)
	}
}()
```

## 🧪 Testing Strategy

### Test-Driven Development (TDD)

1. **Write the test first** - Define expected behavior before implementation
2. **Watch it fail** - Ensure the test actually tests something
3. **Write minimal code** - Just enough to make the test pass
4. **Refactor** - Improve code while keeping tests green
5. **Repeat** - One test at a time

### Table-Driven Tests (the Go standard)

```go
func TestCalculateDiscount(t *testing.T) {
	tests := []struct {
		name    string
		price   float64
		percent float64
		want    float64
		wantErr error
	}{
		{name: "twenty percent off", price: 100, percent: 20, want: 80},
		{name: "zero discount", price: 100, percent: 0, want: 100},
		{name: "negative percent rejected", price: 100, percent: -5, wantErr: ErrInvalidDiscount},
		{name: "over hundred percent rejected", price: 100, percent: 150, wantErr: ErrInvalidDiscount},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := CalculateDiscount(tt.price, tt.percent)
			if tt.wantErr != nil {
				if !errors.Is(err, tt.wantErr) {
					t.Fatalf("CalculateDiscount() error = %v, want %v", err, tt.wantErr)
				}
				return
			}
			if err != nil {
				t.Fatalf("CalculateDiscount() unexpected error: %v", err)
			}
			if got != tt.want {
				t.Errorf("CalculateDiscount() = %v, want %v", got, tt.want)
			}
		})
	}
}
```

### Testing Best Practices

- **Always run with `-race`** locally and in CI — data races are bugs even if they haven't bitten yet.
- **Mark helpers with `t.Helper()`** so failures report the caller's line.
- **Use `t.Cleanup()`** instead of manual teardown, and `t.TempDir()` for scratch directories.
- **Prefer the standard library** for assertions; `github.com/google/go-cmp/cmp` for deep struct diffs. If the project already uses `testify`, follow suit — consistency beats preference.
- **Fake at your own interfaces** — define small interfaces at the consumer and hand-write fakes; avoid heavyweight mock generators unless already established in the repo.
- **Test through the public API** of a package; test internals only when the algorithm warrants it.
- **Put fixtures in `testdata/`** — the go tool ignores that directory.
- Aim for **80%+ coverage on critical paths**; do not chase 100% through trivial getters.

### Test Organization

- Unit tests: `foo_test.go` next to `foo.go`, same package (white-box) or `package foo_test` (black-box, preferred for public API tests)
- Integration tests: guard with `testing.Short()` or build tags, keep them runnable with one command
- Benchmarks: `func BenchmarkXxx(b *testing.B)` — use `b.Loop()` (Go 1.24+) for iteration

## 🔄 Concurrency (Correct First, Fast Second)

### Rules

- **Every goroutine must have a known exit path.** Before writing `go func()`, answer: how does this goroutine stop, and who waits for it? Leaked goroutines are memory leaks.
- **Propagate `context.Context`** through every blocking call chain; honor cancellation with `select`.
- **Channels transfer ownership; mutexes guard state.** Use a `sync.Mutex` for a shared map or counter — don't force channels where a lock is simpler.
- **Use `golang.org/x/sync/errgroup`** for parallel fan-out with error propagation:

```go
func fetchAll(ctx context.Context, urls []string) ([]Result, error) {
	g, ctx := errgroup.WithContext(ctx)
	results := make([]Result, len(urls))

	for i, url := range urls {
		g.Go(func() error {
			res, err := fetch(ctx, url)
			if err != nil {
				return fmt.Errorf("fetch %s: %w", url, err)
			}
			results[i] = res
			return nil
		})
	}

	if err := g.Wait(); err != nil {
		return nil, err
	}
	return results, nil
}
```

- **Limit concurrency** with `errgroup.SetLimit(n)` or a buffered-channel semaphore — never unbounded goroutine-per-item over untrusted input sizes.
- **The race detector is the referee**: `go test -race ./...` must pass. A test that only fails under `-race` is a real bug.
- **Do NOT add concurrency speculatively.** Sequential code that meets requirements beats concurrent code that might.

## 🔧 Configuration Management

### Environment Variables and Settings

Load configuration once at startup in `main`, validate it, and pass it down explicitly — no global config access from business logic.

```go
package config

import (
	"fmt"
	"os"
	"strconv"
	"time"
)

type Config struct {
	AppName     string
	Debug       bool
	DatabaseURL string
	HTTPAddr    string
	Timeout     time.Duration
}

func Load() (Config, error) {
	cfg := Config{
		AppName:  envOr("APP_NAME", "myapp"),
		HTTPAddr: envOr("HTTP_ADDR", ":8080"),
		Timeout:  30 * time.Second,
	}

	cfg.DatabaseURL = os.Getenv("DATABASE_URL")
	if cfg.DatabaseURL == "" {
		return Config{}, fmt.Errorf("DATABASE_URL is required")
	}

	if v := os.Getenv("DEBUG"); v != "" {
		debug, err := strconv.ParseBool(v)
		if err != nil {
			return Config{}, fmt.Errorf("parse DEBUG: %w", err)
		}
		cfg.Debug = debug
	}

	return cfg, nil
}

func envOr(key, fallback string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return fallback
}
```

For larger projects, `github.com/kelseyhightower/envconfig` or `github.com/caarlos0/env` are acceptable — but only if already in `go.mod` or genuinely needed.

## 📊 Logging Strategy

Use the standard library's structured logger, `log/slog`. Do not add third-party logging frameworks to new code.

```go
import "log/slog"

// In main: configure once, inject everywhere.
logger := slog.New(slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{
	Level: slog.LevelInfo,
}))
slog.SetDefault(logger)

// Log with structured context — key-value pairs, not fmt.Sprintf.
slog.InfoContext(ctx, "payment processed",
	"user_id", user.ID,
	"amount", amount,
	"currency", "USD",
	"duration", time.Since(start),
)

// Errors carry the error value.
slog.ErrorContext(ctx, "payment failed", "error", err, "user_id", user.ID)
```

- Log at the edge (handlers, main loops) — deep library code returns errors instead of logging.
- Never log secrets, tokens, or full request bodies.

## 🏗️ Data Types and Validation

### Struct Design

```go
// User is the domain model. Make the zero value meaningful where possible.
type User struct {
	ID        string    `json:"id"`
	Email     string    `json:"email"`
	Name      string    `json:"name"`
	CreatedAt time.Time `json:"created_at"`
	IsActive  bool      `json:"is_active"`
}

// Validate enforces invariants. Call it at construction boundaries
// (API handlers, decoders), not repeatedly in business logic.
func (u *User) Validate() error {
	if u.Email == "" {
		return &ValidationError{Field: "email", Reason: "must not be empty"}
	}
	if !strings.Contains(u.Email, "@") {
		return &ValidationError{Field: "email", Reason: "invalid format"}
	}
	return nil
}
```

- **Validate all external input** (HTTP bodies, CLI flags, DB rows) at the boundary. `github.com/go-playground/validator` is acceptable for tag-based validation if already in use.
- **Use generics judiciously** (type parameters shine for containers and algorithms) — do not genericize code with a single concrete use.
- **`any` (`interface{}`) is a code smell** outside serialization boundaries — reach for a concrete type or a small interface first.

## 🔄 Git Workflow

### Branch Strategy

- `main` - Production-ready code
- `develop` - Integration branch for features
- `feature/*` - New features
- `fix/*` - Bug fixes
- `docs/*` - Documentation updates
- `refactor/*` - Code refactoring
- `test/*` - Test additions or fixes

### Commit Message Format

Never include claude code, or written by claude code in commit messages

```
<type>(<scope>): <subject>

<body>

<footer>
```

Types: feat, fix, docs, style, refactor, test, chore

Example:

```
feat(auth): add two-factor authentication

- Implement TOTP generation and validation
- Add QR code generation for authenticator apps
- Update user model with 2FA fields

Closes #123
```

## 🛡️ Security Best Practices

### Security Guidelines

- **Never commit secrets** - use environment variables or a secrets manager
- **Run `govulncheck ./...`** in CI - it reports only vulnerabilities your code actually reaches
- **Use parameterized queries** for all database operations - never build SQL with string concatenation
- **Use `crypto/rand`** for anything security-sensitive - `math/rand/v2` is not cryptographically secure
- **Hash passwords with bcrypt or argon2** (`golang.org/x/crypto`)
- **Set timeouts on all HTTP servers and clients** - the zero-value `http.Server` has none

```go
// Parameterized query — the only acceptable form.
row := db.QueryRowContext(ctx,
	"SELECT id, email FROM users WHERE id = $1", userID)

// HTTP server with sane timeouts.
srv := &http.Server{
	Addr:              cfg.HTTPAddr,
	Handler:           mux,
	ReadHeaderTimeout: 5 * time.Second,
	ReadTimeout:       10 * time.Second,
	WriteTimeout:      30 * time.Second,
	IdleTimeout:       120 * time.Second,
}

// Secure random token.
func generateToken(n int) (string, error) {
	b := make([]byte, n)
	if _, err := rand.Read(b); err != nil {
		return "", fmt.Errorf("generate token: %w", err)
	}
	return base64.URLEncoding.EncodeToString(b), nil
}
```

## 🚀 Performance Considerations

### Optimization Guidelines

- **Profile before optimizing** - use `go test -bench`, `pprof`, and `go tool trace`; never optimize on intuition
- **Preallocate slices** when the size is known: `make([]T, 0, n)`
- **Pass large structs by pointer**; pass small structs by value - measure when unsure
- **Reuse buffers** with `sync.Pool` only in proven hot paths
- **`strings.Builder`** for string concatenation in loops
- Use `go build -pgo=auto` with a production profile for free wins on hot services

```go
// Benchmark example (Go 1.24+ b.Loop)
func BenchmarkProcessOrder(b *testing.B) {
	order := makeTestOrder()
	for b.Loop() {
		processOrder(order)
	}
}
```

## 📋 Pre-commit Checklist (MUST COMPLETE ALL)

- [ ] `gofmt -l .` reports no files (code is formatted)
- [ ] `go build ./...` succeeds
- [ ] `go vet ./...` passes
- [ ] `golangci-lint run` passes
- [ ] `go test -race ./...` passes
- [ ] `go mod tidy` produces no diff
- [ ] `govulncheck ./...` shows no reachable vulnerabilities
- [ ] No ignored errors without a `// Reason:` comment
- [ ] All exported identifiers have doc comments
- [ ] Commit message follows Conventional Commits (`feat:`, `fix:` ...)

## ⚠️ Critical Guidelines (Non-Negotiable)

1. **NEVER ignore an error** - handle it, wrap it with `%w`, or document why not with `// Reason:`
2. **NEVER panic in library code** - return errors; `panic` only for impossible states
3. **MUST run `go test -race ./...`** before every commit - races are bugs
4. **MUST pass `go vet` and `golangci-lint`** with zero findings
5. **NEVER edit `go.mod`/`go.sum` by hand** - use `go get` and `go mod tidy`
6. **MUST propagate `context.Context`** as the first parameter through call chains
7. **NEVER store secrets in code** - environment variables or secret managers only
8. **MUST keep `main.go` thin** - wiring only, logic lives in `internal/`
9. **NEVER launch a goroutine without a defined exit path** and owner
10. **MINIMUM 80% coverage on critical paths** - enforce in CI

## 📚 Useful Resources

### Essential Tools

- golangci-lint: https://golangci-lint.run/
- gofumpt: https://github.com/mvdan/gofumpt
- govulncheck: https://pkg.go.dev/golang.org/x/vuln/cmd/govulncheck
- go-cmp: https://github.com/google/go-cmp
- errgroup: https://pkg.go.dev/golang.org/x/sync/errgroup

### Go Best Practices

- Effective Go: https://go.dev/doc/effective_go
- Go Code Review Comments: https://go.dev/wiki/CodeReviewComments
- Google Go Style Guide: https://google.github.io/styleguide/go/
- Standard library docs: https://pkg.go.dev/std
- Go Proverbs: https://go-proverbs.github.io/

## ⚠️ Important Notes

- **NEVER ASSUME OR GUESS** - When in doubt, ask for clarification
- **Always verify import paths and module names** before use
- **Keep CLAUDE.md updated** when adding new patterns or dependencies
- **Test your code** - No feature is complete without tests
- **Document your decisions** - Future developers (including yourself) will thank you

## 🔍 Search Command Requirements

**CRITICAL**: Always use `rg` (ripgrep) instead of traditional `grep` and `find` commands:

```bash
# ❌ Don't use grep
grep -r "pattern" .

# ✅ Use rg instead
rg "pattern"

# ❌ Don't use find with name
find . -name "*.go"

# ✅ Use rg with file filtering
rg --files | rg "\.go$"
# or
rg --files -g "*.go"
```

**Enforcement Rules:**

```
(
    r"^grep\b(?!.*\|)",
    "Use 'rg' (ripgrep) instead of 'grep' for better performance and features",
),
(
    r"^find\s+\S+\s+-name\b",
    "Use 'rg --files | rg pattern' or 'rg --files -g pattern' instead of 'find -name' for better performance",
),
```

## 🚀 GitHub Flow Workflow Summary

main (protected) ←── PR ←── feature/your-feature
↓ ↑
deploy development

### Daily Workflow:

1. git checkout main && git pull origin main
2. git checkout -b feature/new-feature
3. Make changes + tests
4. git push origin feature/new-feature
5. Create PR → Review → Merge to main

---

_This document is a living guide. Update it as the project evolves and new patterns emerge._
