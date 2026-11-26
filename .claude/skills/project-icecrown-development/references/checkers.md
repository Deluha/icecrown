# Checkers

What each guard under `tools/` parses and enforces. Their tests live in `tests/tools/`. Each
checker prints one line per violation (`path:line: CODE message`) and exits 1 if there is any.

## check_conventions.py

Parses every Python file under `src/icecrown/` with `ast` (C5 walks the whole repository). Covers
only what `ruff` and `mypy` cannot express.

| Code | Rule | Source |
|---|---|---|
| C1 | No `print()` call and no `sys.stdout` / `sys.stderr` access outside `_messages.py` | R2 |
| C2 | In the fingerprint path (`_types.py`, `_canon.py`, `_fingerprint.py`, `_soul.py`): no import of `time`, `random`, `secrets`, `uuid`, `os`, `platform`, `locale`, `getpass`; no call of the builtin `hash()` or `id()`; no `.now()`, `.today()` or `.utcnow()` call | R3 |
| C3 | No network module imported anywhere in `src/`: `socket`, `ssl`, `http.client`, `http.server`, `urllib.request`, `ftplib`, `smtplib`, `requests`, `httpx`, `aiohttp`, `urllib3` | R5 |
| C4 | Every top-level module or package of `icecrown` is private (`_*`) unless it is `__init__.py`, `__main__.py` or an entry point declared in `pyproject.toml`; every function in an entry-point module is at most 40 lines | R8 |
| C5 | No `test_*.py`, `*_test.py` or `conftest.py` outside `tests/` (tracked and untracked files, ignored ones excluded) | R4 |
| C6 | A module-level name ending in `_VERSION` is assigned only in `_versions.py` | R1, R6 |
| C7 | `icecrown/__init__.py` declares `__all__` as a literal list; every name in it is defined or imported there and has a docstring where it is defined. Sorting is ruff's RUF022 | R8 |

The entry points come from `[project.scripts]` and `[project.entry-points.pytest11]`; the checker
reads them from `pyproject.toml` rather than keeping its own list (R1).

## check_guidance_integrity.py

Parses the guidance Markdown: `CLAUDE.md`, `README.md`, `CONTRIBUTING.md`, `tests/README.md` and
every `.md` under `.claude/`.

| Code | Rule |
|---|---|
| G1 | Every relative Markdown link resolves to a file, and every `#anchor` to a heading in it (GitHub slug rules) |
| G2 | `CLAUDE.md` is at most 80 lines and 8 KiB |
| G3 | The skill's `SKILL.md` routing table has exactly one row per file under `references/`, and nothing else links into `references/` from that table twice |
| G4 | A rule in `.claude/rules/` has a `paths` list in its frontmatter and at most 6 non-blank body lines, each holding a link (pointer-only) |
| G5 | A command skill (every skill but the development skill) has `name` and `description` and at most 6 non-blank body lines, each holding a link |
| G6 | An agent in `.claude/agents/` declares `name`, `description`, `tools`, `model` and `effort`, and its `model` and `effort` match its row in [recipes.md](recipes.md#roles) |
| G7 | `evals/evals.json` parses, and every eval has an `id`, a `prompt` and an `expect` naming a routed file or an ask-first item |

## check_docs_sync.py

Maps code areas to the doc that must change with them (R7):

| Area | Its doc |
|---|---|
| `src/icecrown/` | anything under `docs/` |
| `tools/` | this file |
| `.github/workflows/`, `.pre-commit-config.yaml`, `.claude/hooks/` | [qa-and-ci.md](qa-and-ci.md) |

A doc changed anywhere in the checked set counts for the whole set, so code and its doc may land in
different commits of one pull request. A line that is exactly `[skip-docs]` in a commit body waives
the check for that commit's files only.

| Mode | Checks | Used by |
|---|---|---|
| `--commit-msg <file>` | the staged files, with the message being written | the commit-msg hook |
| `--range <base>..<head>` | every commit in the range | `ci-docs-sync` |
| `--base <ref>` | the commits since the merge base with `<ref>`, plus uncommitted and untracked files | `verify` (against `origin/main`, else `main`; skipped if neither exists) |

## verify.py

Runs, in order: the three checkers, `ruff check`, `ruff format --check`, `mypy`, and
`coverage run -m pytest` followed by the coverage report with its threshold. Prints one table (row,
result, seconds) and the output of every failing row. See [qa-and-ci.md](qa-and-ci.md#verify).
