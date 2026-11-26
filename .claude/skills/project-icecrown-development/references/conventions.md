# Conventions

The rules every code change follows. `CLAUDE.md` carries their short form; this file is the full
form. What a checker enforces mechanically is in [checkers.md](checkers.md).

## Hard rules

**R1 — Registries are imported, never hardcoded.** Sources, logical types and format versions each
have one registry module (see [architecture.md](architecture.md#module-map)). Code that needs a
source name, a type tag or a version imports it from there. *Why:* a value written in two places
drifts. *Checked:* C6 for version constants; review for the rest.

**R2 — Shared helpers are reused, never re-implemented.** Before writing a helper, grep for one
([recipes.md](recipes.md#grep-before-coding)). Console output goes through the message helpers in
`icecrown._messages` ([style.md](style.md#console-messages)). *Why:* one behaviour per concern, one
place to fix it. *Checked:* C1 for output; review for the rest.

**R3 — Nothing non-deterministic in a fingerprint path.** The fingerprint depends on the data and the
recorded capture options only: no wall-clock time, randomness, environment variables, locale,
process-salted `hash()`, dictionary or set iteration order, platform or library-version behaviour.
*Why:* the same data must give the same fingerprint on every supported machine. *Checked:* C2, and
the golden fingerprints pinned across the CI matrix.

**R4 — No files the user didn't ask for; every test lives under `tests/`.** No stray notes, scripts,
summaries or example files. Scribe notes stay outside the repository tree. *Checked:* C5 for tests.

**R5 — The core is offline, and so are the tests.** No network call anywhere in `src/`. A database is
reached only through a connection the user supplies. Tests run with sockets disabled
(`pytest-socket`); none touches a live database. *Checked:* C3, and `--disable-socket` in the pytest
configuration.

**R6 — Format changes are versioned.** The store-format version (file layout) and the
fingerprint-spec version (how bytes are hashed) are separate. Changing either bumps its version,
updates the published spec or reference and its test vectors, and — from the 0.1.0 tag on — ships a
migration or a clear "freeze again" error with a compatibility test. Follow
[changing-the-fingerprint.md](workflows/changing-the-fingerprint.md) or
[changing-the-store-format.md](workflows/changing-the-store-format.md). *Why:* a baseline committed
today must still be readable, or refused clearly, tomorrow.

**R7 — Docs move with the code.** A change in a documented area changes its doc in the same pull
request. *Checked:* `check_docs_sync.py`; `[skip-docs]` on its own line in a commit body is the
escape hatch, for changes with no user-visible effect.

**R8 — Entry points hold only their flow.** The CLI (`icecrown/__main__.py`) and the pytest plugin
parse arguments, call private modules and map results to output and exit codes. Logic lives in
private `_*.py` modules. The public API is exactly what `icecrown/__init__.py` lists in `__all__`.
*Checked:* C4 and C7.

## Ask first

Stop and ask the owner, in the [decision format](recipes.md#decision-format), before changing:

| Item | Why it is gated |
|---|---|
| The fingerprint spec: canonicalisation, hash, combination | Users' committed baselines depend on it |
| The store layout and the baseline-file format | Same, and it is a published format |
| Default tolerances and exit codes | CI pipelines branch on them |
| Public API and CLI signatures | The compatibility promise covers them |
| A new runtime dependency or a changed lower bound | Every user installs it |
| Publishing a release | Public and irreversible |
| The guidance machinery and CI (`CLAUDE.md`, `.claude/settings.json`, `.claude/agents/`, `.claude/hooks/`, `.github/workflows/`, `.pre-commit-config.yaml`, `.gitleaks.toml`) | They govern every later change |

`.claude/settings.json` turns most of these into permission prompts; the list here binds even where
no prompt appears.

## Module layout

- `src/` layout: the package is `src/icecrown/`, so tests import the installed package, never the
  checkout.
- One concept per private module; a module that grows a second concept splits.
- `icecrown/__init__.py` re-exports the public names and declares `__all__`; nothing else is public.
- Optional dependencies (`pandas`, `sqlalchemy`) are imported lazily inside the adapter that needs
  them. A missing extra raises an error naming the extra: `pip install "icecrown[pandas]"`.
- Tests mirror the module they cover: `tests/test_<module>.py`; checker tests live in `tests/tools/`.

## Error handling

- Every error the library raises derives from `IcecrownError` in `icecrown._errors`; the public
  hierarchy is part of the compatibility promise.
- A message says what happened, why, and what to do next.
- A message never holds a secret (a connection URL, a token) and, by default, no cell value.
- Third-party exceptions are wrapped at the boundary: `raise SourceReadError(...) from err`.
- No bare `except`, no `except Exception: pass`. Catch the narrowest type.
- Validate input at the public boundary; private code may assume valid input.

## Typing

- `mypy --strict` passes on `src/`, `tools/`, `tests/` and the hooks.
- No `Any` in a public signature. A `# type: ignore[code]` names its code and carries a reason.

## Simplicity audit

Before the `reviewer` runs, the author answers each question for the diff:

1. Is there code that nothing calls yet?
2. Is there a parameter, option or abstraction with a single use?
3. Does a helper duplicate one that exists?
4. Can a branch, a class or a module go without losing a requirement?
5. Is every comment still true, and does it say *why*?
6. Did the change touch anything outside its stated scope?
