# Project Icecrown — operating contract

Snapshot testing for tabular data ([README.md](README.md)). The plan is [ROADMAP.md](ROADMAP.md);
what shipped is `CHANGELOG.md`. Every task routes through the skill
[project-icecrown-development](.claude/skills/project-icecrown-development/SKILL.md): find the task's
row, read the one file it names, follow it.

## Operating principles

1. **Flag uncertainties — ask, don't assume.** Validate a request against the repository's patterns
   and flag a conflict instead of silently complying.
2. **Roles.** The session designs, signs off, writes briefs and owns the ask-first gates and the done
   gate: it reads the diff and runs the verify command itself. The `implementer` writes, the `reader`
   reads, the `reviewer` reviews. A small edit (one file, about 20 changed lines, no ask-first item,
   no new logic) the session makes itself. Roles and briefs:
   [recipes.md](.claude/skills/project-icecrown-development/references/recipes.md#roles).
3. **Be concise** — but never drop a confidence label on an architectural call, a pattern-conflict
   flag, or a better approach when one exists.
4. **Modular, one source of truth.** Surgical changes over sweeping refactors. A pointer replaces a
   second copy of a fact.

## Hard rules

Short form; the full form and its reasons are in
[conventions.md](.claude/skills/project-icecrown-development/references/conventions.md#hard-rules).

- **R1** Registries (sources, logical types, format versions) are imported, never hardcoded.
- **R2** Shared helpers are reused, never re-implemented; console output goes through the message
  helpers.
- **R3** Nothing non-deterministic in a fingerprint path.
- **R4** No files the user didn't ask for; every test lives under `tests/`.
- **R5** The core is offline, and so are the tests.
- **R6** A store-format or fingerprint-spec change bumps its version, updates the published spec and
  its test vectors, and — from the 0.1.0 tag on — ships a migration or a clear "freeze again" error
  with a compatibility test.
- **R7** Docs move with the code.
- **R8** Entry points hold only their flow; logic lives in private `_*.py` modules; the public API is
  what `icecrown/__init__.py` exports.

## Ask first

Stop and ask the owner before changing any of these
([why](.claude/skills/project-icecrown-development/references/conventions.md#ask-first)):

- the fingerprint spec (canonicalisation, hash, combination);
- the store layout and the baseline-file format;
- default tolerances and exit codes;
- public API and CLI signatures;
- a new runtime dependency or a changed lower bound;
- publishing a release;
- the guidance machinery and CI: `CLAUDE.md`, `.claude/settings.json`, `.claude/agents/`,
  `.claude/hooks/`, `.github/workflows/`, `.pre-commit-config.yaml`, `.gitleaks.toml`.

## Workflow for any change

1. Understand the request; restate it if it is ambiguous.
2. Route through the skill and read the routed file.
3. Grep the established pattern before writing new code.
4. Validate against the rules above; flag conflicts.
5. Implement (or brief the `implementer`).
6. Verify: `uv run python tools/verify.py` — one pass/fail table.
7. Update the changed area's docs (R7).
8. Simplicity audit, then the `reviewer` agent on every non-trivial diff.
