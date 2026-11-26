# QA and CI

The gates every change passes, where each one runs, and the support matrix.

## Verify

```bash
uv run python tools/verify.py
```

One command runs every gate a pull request needs and prints one pass/fail table: the three checkers
([checkers.md](checkers.md)), `ruff check`, `ruff format --check`, `mypy` and the test suite with
branch coverage. It exits non-zero if any row fails. `--only <name>` runs one row; `--list` names
them. A contributor needs nothing else; CI runs the same gates.

## Gates

| Gate | Tool | Local hook | `verify` | CI |
|---|---|---|---|---|
| Lint | `ruff check` | pre-commit | yes | `ci-pre-commit` |
| Format | `ruff format` | pre-commit | yes | `ci-pre-commit` |
| Types | `mypy --strict` | pre-commit | yes | `ci-pre-commit` |
| Secrets | gitleaks | pre-commit (staged) | — | `ci-pre-commit` (all files and the full history) |
| Conventions | `tools/check_conventions.py` | pre-commit | yes | `ci-pre-commit` |
| Guidance integrity | `tools/check_guidance_integrity.py` | pre-commit | yes | `ci-pre-commit` |
| Docs sync | `tools/check_docs_sync.py` | commit-msg | yes | `ci-docs-sync` |
| Tests and coverage | pytest, coverage | — | yes | `ci-tests` |
| Build and wheel tests | `uv build`, `twine check --strict` | — | — | `ci-build` |
| Docs build | Sphinx, warnings as errors | — | — | `ci-docs` |
| Workflow lint | actionlint, zizmor | — | — | `ci-workflow-lint` |

## Tests

- Every test lives under `tests/` (R4); checker tests under `tests/tools/`.
- Tests import the installed package (`src/` layout). `ci-build` runs the suite against the built
  wheel.
- Offline (R5): `--disable-socket` is in the pytest configuration; Unix sockets stay allowed for
  local inter-process use. No test reaches a live database; SQL tests use in-memory SQLite.
- Warnings are errors; markers are strict; tests import in `importlib` mode.
- Hypothesis: the `dev` profile locally, `ci` in CI (`HYPOTHESIS_PROFILE=ci`: derandomised, no
  example database, more examples).
- Coverage: branch coverage of `icecrown`, at least 90 %, combined across the CI matrix.
- Golden fingerprints (Phase 1) are pinned values that every matrix cell must reproduce.
- Benchmarks are opt-in and never a CI gate.

## Support matrix

Every CPython version that is not end-of-life, from 3.11: today 3.11–3.15.

| Job | Python | Runners |
|---|---|---|
| Tests | 3.11, 3.12, 3.13, 3.14, 3.15 | `ubuntu-24.04` |
| Tests | 3.11, 3.15 | `macos-15` (arm64), `windows-2025` |
| Tests | 3.15 | `ubuntu-24.04-arm` |
| Lowest bounds (`--resolution lowest-direct`) | 3.11 | `ubuntu-24.04` |
| Pre-release dependencies (non-blocking) | 3.15 | `ubuntu-24.04` |
| Next Python (`3.16-dev`, non-blocking) | 3.16 | `ubuntu-24.04` |

Runner labels are pinned, never `-latest`. A runner image retirement is a CI change (ask first).

## CI workflows

All under `.github/workflows/`; every action pinned to a commit hash, token permissions declared
at the top of each workflow.

| Workflow | Trigger | What it does |
|---|---|---|
| `ci-pre-commit.yml` | pull request, push to `main` | Every pre-commit hook on all files |
| `ci-docs-sync.yml` | pull request | `check_docs_sync.py` over the pull request's commits |
| `ci-tests.yml` | pull request, push to `main` | The support matrix, the bound jobs, combined coverage, and `CI gate`, which fails unless the matrix, the lowest-bound job and coverage succeeded |
| `ci-build.yml` | pull request, push to `main` | sdist and wheel, `twine check --strict`, tests against the installed wheel on 3.11 and 3.15 |
| `ci-docs.yml` | pull request, push to `main` | The documentation site, warnings as errors |
| `ci-workflow-lint.yml` | pull request touching `.github/` | actionlint and zizmor |
| `codeql.yml` | pull request, push to `main`, weekly | CodeQL code scanning (Python and Actions) |
| `dependency-review.yml` | pull request | Blocks a dependency with a known vulnerability |
| `scorecard.yml` | push to `main`, weekly | OpenSSF Scorecard |
| `release.yml` | tag `v*` | Build, attest, publish behind an approval gate, GitHub Release |

## Hooks

- **Git hooks** (`.pre-commit-config.yaml`): the pre-commit stage runs file hygiene, ruff, mypy,
  gitleaks, `check_conventions.py` (when package, tool or test files change) and
  `check_guidance_integrity.py` (when Markdown, `.claude/` or `evals/` change); the commit-msg stage
  runs `check_docs_sync.py --commit-msg` on every commit. Python tools run from `uv.lock`
  through `uv run --frozen`, so their versions never drift from CI.
- **Claude Code hooks** (`.claude/hooks/`): `session-start.sh` syncs the environment and installs
  the git hooks in cloud sessions (skip with `ICECROWN_SKIP_DEV_SETUP=1`); `post_edit_check.py`
  runs `ruff check` on a Python file after an edit and reports a failure back to the session.
