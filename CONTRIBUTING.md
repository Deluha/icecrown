# Contributing to Project Icecrown

Thank you for helping. This page is all a human contributor needs; the agent machinery under
`.claude/` is optional for humans and is described in [CLAUDE.md](CLAUDE.md).

## Set up

You need [uv](https://docs.astral.sh/uv/) and git.

```bash
git clone https://github.com/Deluha/icecrown.git
cd icecrown
uv sync
uv run pre-commit install
```

`uv sync` creates `.venv/` from `uv.lock` with the test and lint tools; the git hooks then run the
linters, the type checker, the secret scan and the checkers on every commit.

## The one command

```bash
uv run python tools/verify.py
```

It runs the convention, guidance and docs-sync checkers, `ruff`, `mypy` and the tests with branch
coverage, and prints one pass/fail table. `--list` names the steps and `--only <step>` runs one. The
git hooks add the file-hygiene checks and the secret scan; CI adds the platform matrix, the build,
the docs build and workflow lint.

## Making a change

1. For anything beyond a small fix, open an issue first. Some changes need the owner's decision
   before code is written: the fingerprint specification, the store format, default tolerances and
   exit codes, public API and command signatures, runtime dependencies, and CI. The full list and the
   reasons are in the
   [conventions](.claude/skills/project-icecrown-development/references/conventions.md#ask-first).
2. Follow the [conventions](.claude/skills/project-icecrown-development/references/conventions.md#hard-rules)
   and the [style guide](.claude/skills/project-icecrown-development/references/style.md). Tests live
   under `tests/` ([tests/README.md](tests/README.md)) and never touch the network.
3. Update the documentation of what you changed, and add an entry under "Unreleased" in
   `CHANGELOG.md`. A change in a documented area without its doc fails the docs-sync check; write
   `[skip-docs]` on its own line in the commit body when there is genuinely nothing to document.
4. Commit messages: an imperative subject of at most 72 characters; a body that explains why.
5. Open a pull request and fill in its template.

## Building the documentation

```bash
uv run --group docs sphinx-build -W --keep-going -n -b html docs docs/_build/html
```

Sphinx needs Python 3.13 or newer for this step.

## Conduct and security

Everyone taking part follows the [code of conduct](CODE_OF_CONDUCT.md). Report a vulnerability
privately, as described in [SECURITY.md](SECURITY.md), never in a public issue.
