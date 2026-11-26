# Checkers

What each guard under `tools/` parses and enforces. Their tests live in `tests/tools/`. Each
checker prints one line per violation (`path:line: CODE message`) and exits 1 if there is any.

## check_conventions.py

Parses every Python file under `src/icecrown/` with `ast` (C5 walks the whole repository). Covers
only what `ruff` and `mypy` cannot express.

| Code | Rule | Source |
|---|---|---|
| C1 | No `print()` call and no `sys.stdout`, `sys.stderr`, `sys.__stdout__` or `sys.__stderr__` access (also through an alias of `sys`) outside `_messages.py` | R2 |
| C2 | In the [fingerprint path](architecture.md#module-map) (those modules, or packages of the same name): no import of `time`, `random`, `secrets`, `uuid`, `os`, `platform`, `locale`, `getpass`; no call of the builtin `hash()` or `id()`; no `.now()`, `.today()` or `.utcnow()` call | R3 |
| C3 | No network module imported anywhere in `src/`: `socket`, `ssl`, `http.client`, `http.server`, `urllib.request`, `ftplib`, `smtplib`, `requests`, `httpx`, `aiohttp`, `urllib3` | R5 |
| C4 | Every top-level module or package of `icecrown` is private (`_*`) unless it is `__init__.py`, `__main__.py` or an entry point declared in `pyproject.toml`; every function in an entry-point module or package is at most 40 lines | R8 |
| C5 | No `test_*.py`, `*_test.py` or `conftest.py` outside `tests/` (tracked and untracked files, ignored ones excluded) | R4 |
| C6 | A module-level name ending in `_VERSION` (including tuple targets and assignments inside module-level `if`, `try` and `with` blocks; reading one, as in `TABLE[SPEC_VERSION] = …`, is fine) is assigned only in `_versions.py` | R1, R6 |
| C7 | `icecrown/__init__.py` declares `__all__` as a literal list; every name in it is defined or imported there and has a docstring where it is defined (an imported module counts as documented here; its own docstring is its module's business). Sorting is ruff's RUF022 | R8 |

The entry points come from `[project.scripts]` and `[project.entry-points.pytest11]`; the checker
reads them from `pyproject.toml` rather than keeping its own list (R1).

## check_guidance_integrity.py

Parses the guidance Markdown: `CLAUDE.md`, `README.md`, `CONTRIBUTING.md`, `tests/README.md` and
every `.md` under `.claude/`.

| Code | Rule |
|---|---|
| G1 | Every relative Markdown link resolves to a file inside the repository, and every `#anchor` to a heading in it (GitHub slug rules: code and link text kept, punctuation dropped, repeats numbered). Links inside code spans and fenced blocks are ignored |
| G2 | `CLAUDE.md` is at most 80 lines and 8 KiB |
| G3 | The skill's `SKILL.md` routing table has exactly one row per file under `references/`; links that leave the skill (to `docs/`, say) are allowed and are not routes |
| G4 | A rule in `.claude/rules/` has a `paths` list in its frontmatter and at most 6 non-blank body lines, each holding a link (pointer-only) |
| G5 | A command skill (every skill but the development skill) has `name` and `description` and at most 6 non-blank body lines, each holding a link |
| G6 | An agent in `.claude/agents/` declares `name`, `description`, `tools`, `model` and `effort`, and its `model` and `effort` match its row in [recipes.md](recipes.md#roles); `.claude/settings.json` parses and its `model` and `effortLevel` match the session's row |
| G7 | `evals/evals.json` exists and parses; every eval has a unique `id`, a `prompt`, and an `expect` that is either a file the routing table routes to or `ask-first: <item>`, where the item (up to any parenthesis) appears in the [ask-first list](conventions.md#ask-first) |

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
| `--base <ref>` | the commits since the merge base with `<ref>`, plus uncommitted and untracked files | `verify` (against `origin/main`, else `main`; skipped when neither has a merge base with `HEAD`, as in a shallow clone) |

`ci-docs-sync` does not run on Dependabot's pull requests, which only move pins and the lockfile;
a skipped required check counts as passed.

Paths are read unquoted, so non-ASCII file names match their area. A git failure (an unknown ref, a
clone too shallow for the range) exits 2 with the reason instead of a traceback.

## release_notes.py

Not a checker but a release helper, run by `release.yml`. `release_notes.py <tag>` fails unless the
tag is `v` plus the version in `pyproject.toml` and `CHANGELOG.md` has a `## [<version>]` entry; a
pre-release without one (a `.devN` rehearsal) gets the `## [Unreleased]` section. It prints the
entry, which becomes the GitHub Release notes. `--is-prerelease` only answers through its exit code.

## verify.py

Runs, in order: the three checkers, `ruff check`, `ruff format --check`, `mypy`, and
`coverage run -m pytest` followed by the coverage report with its threshold. Prints one table (row,
result, seconds) and the output of every failing row. See [qa-and-ci.md](qa-and-ci.md#verify).
