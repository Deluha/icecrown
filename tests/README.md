# Tests

Every test lives here (hard rule R4). The rules for writing them are in
[qa-and-ci.md](../.claude/skills/project-icecrown-development/references/qa-and-ci.md#tests).

## Layout

| Path | Covers |
|---|---|
| `tests/test_<module>.py` | The package, one file per module it covers |
| `tests/tools/` | The checkers, the verify command, the release-notes tool and the Claude Code hooks |
| `tests/conftest.py` | Shared configuration: the Hypothesis profiles |

## Running

```bash
uv run pytest                          # the suite
uv run python tools/verify.py          # the suite with coverage, plus every other gate
HYPOTHESIS_PROFILE=ci uv run pytest    # the CI profile: derandomised, more examples
```

## Rules of thumb

- Tests import the installed package, never the checkout (`src/` layout); `ci-build` runs the suite
  against the built wheel.
- No network: sockets are disabled by `pytest-socket` for every test. SQL tests use in-memory SQLite.
- Warnings are errors. A test that needs a temporary file uses `tmp_path`.
- Benchmarks (from Phase 1) are opt-in and never run by default.
