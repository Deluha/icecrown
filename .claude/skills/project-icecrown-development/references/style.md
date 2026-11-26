# Style

How text in the code and the repository reads. Lint and format rules are in `pyproject.toml` and run
through [the verify command](qa-and-ci.md#verify).

## Docstrings and comments

- Google-style docstrings on every public module, class, function and constant; private code gets
  one when its purpose is not obvious from the name.
- The first line is a sentence in the imperative ("Return the soul of a table.").
- A comment says *why*, never *what*. A comment that restates the code is deleted.
- No commented-out code; no `TODO` without an issue link.

## Console messages

- All console output goes through the helpers in `icecrown._messages` (R2, checker C1).
- Shape: what happened — why — the next step. Example:
  `No baseline for snapshot "orders". Run: icecrown freeze orders`.
- Plain text. Colour and the codename banner appear only on an interactive terminal; logs, CI output
  and `--quiet` runs stay plain.
- Row hashes are never printed. Cell values appear only where the report rules allow
  (Phase 6: `--show-values`).
- Output is bounded: a summary first, then at most a fixed number of detail lines with a count of
  the rest.

## CLI flags

- Long flags in kebab case (`--show-values`); a short flag only for the most common ones (`-q`).
- Shared flags (`--quiet`, `--config`, `--format`, `--output`) mean the same on every command.
- No flag ever carries a secret: no URL flag, no inline SQL. Connections come from environment
  variables only.
- Exit codes are a documented, tested table; a new code is an ask-first item.

## Prose

- British English (licence, canonicalisation, behaviour), short sentences, active voice.
- Headings in sentence case. Markdown wrapped at about 105 characters.
- Every fact lives in one file; link to it instead of restating it.

## Commit messages

- Subject in the imperative, at most 72 characters, no trailing full stop.
- The body explains *why* when it is not obvious; `[skip-docs]` on its own line when R7 does not
  apply.
