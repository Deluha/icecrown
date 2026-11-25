# Project Icecrown — Roadmap

The planned scope of the next release. `RELEASE_NOTES.md` records what shipped; this file records
what is planned. A release's section leaves this file when the release is tagged. Owner decisions are dated.
Every default marked *proposed* below was accepted by the owner on 2026-11-25; the mark is kept to show
which values are defaults a phase may bring back to the owner with a reason, never change on its own.

## What Project Icecrown is

An open-source (MIT) Python toolkit for **snapshot testing of tabular data**: freeze the output of a data
pipeline, and prove later that a code change did not move it — or show exactly which rows, columns and
values moved.

The problem it solves: unit tests cover code, not data. A refactor that "changes nothing" can still shift a
rating, drop forty rows or turn a column from integer to float, and nobody notices until a report looks
wrong. Icecrown gives a pipeline the same safety net a UI gets from snapshot tests:

1. **Freeze** a dataset: capture a deterministic fingerprint (and optionally a frozen copy) as the baseline.
2. **Verify** on every run or pull request: recompute the fingerprint and compare.
3. **Explain** a mismatch: schema diff, keyed row diff, value diff within declared tolerances.
4. **Accept** an intended change explicitly, so the new state becomes the baseline and the change is on record.

Audience: data engineers and analysts with pandas / SQL pipelines who want parity checks in CI without a
data platform. Form: a Python library, a `icecrown` command and a pytest plugin. No server, no account,
no network access.

### Codenames

Each system is named after Icecrown Citadel, and its entry points open with that name in their banner.

| Codename | System | In v0.1 |
|---|---|---|
| **Frostmourne** | **The lead feature.** The snapshot engine: it captures a dataset's *soul* — a canonical, deterministic fingerprint of its schema and content, row by row | Phase 1 |
| **The Frozen Throne** | The snapshot store: the `.icecrown/` directory holding soul manifests, baselines and optional frozen copies | Phase 1 |
| **Light's Hammer** | The foundation: packaging, the guidance machinery, the checkers and CI | Phase 0 |
| **Gunship Battle** | Sources: the adapters that carry data in (DataFrame, CSV, Parquet, SQL query) and the `icecrown` command itself | Phase 2 |
| **Lord Marrowgar** | The schema ("bones") diff: columns added, removed, reordered, retyped | Phase 3 |
| **Blood Prince Council** | The keyed row and value diff: two datasets reconciled into added, removed and changed rows, within tolerances | Phase 4 |
| **Deathbringer Saurfang** | The gate: `verify` / `accept`, exit codes, the pytest plugin — the thing that fails a build | Phase 5 |
| **Lady Deathwhisper** | Reports: the findings as console text, Markdown (for a pull-request comment) and JSON | Phase 6 |
| **The Lich King** | The suite: one `icecrown.toml` that declares every snapshot of a project and runs them all | Phase 7 |
| Festergut | Distribution drift (statistical shift without a row-level baseline) | later |
| Rotface | Rot checks: staleness, null-rate and duplicate growth | later |
| Professor Putricide | Fault injection: mutate a dataset on purpose to prove the checks catch it | later |
| Blood-Queen Lana'thel | Lineage: the bloodline from a snapshot back to the inputs and code version that produced it | later |
| Valithria Dreamwalker | Healing: `thaw` a frozen copy back into a file or table | later |
| Sindragosa | Cold storage: retention, compaction and a remote store | later |

Project Icecrown is an independent open source project, named after the legendary raid as an homage. It is
not affiliated with or endorsed by Blizzard Entertainment, and it has nothing to do with World of Warcraft.

## v0.1 — Frostmourne

Goal: a pip-installable first release in which a user can freeze a dataset, verify it in CI, read a
useful diff when it moved, and accept an intended change. Everything else waits.

### Scope rules

Owner decisions (2026-11-25):

- **Licence.** MIT, open source.
- **Naming.** Every feature is named after Icecrown Citadel; Frostmourne is the lead feature.
- **Process.** Development follows the process set up in Phase 0: an operating contract, a routing skill,
  writer / reader / reviewer agents, mechanical checkers, one verify command, phase-based delivery.
- **This session decided scope only.** No code exists yet; Phase 0 starts the build.

Accepted as proposed (owner, 2026-11-25):

- **Offline and local.** The core makes no network call and needs no service. A database is reached only
  through a connection the user supplies.
- **Deterministic.** The same data gives the same fingerprint on every machine, operating system and
  library version the release supports. No wall-clock time, randomness or environment-dependent ordering
  enters a fingerprint.
- **Small dependency surface.** Python ≥ 3.11; runtime dependencies `pandas` and `pyarrow` only; SQL
  support is an optional extra (`sqlalchemy`). A new runtime dependency is an ask-first change.
- **Data stays private by default.** A soul manifest holds hashes, schema and counts — never cell values.
  A frozen copy of the data is written only when the user asks for it.
- **Not in v0.1.** The *later* codenames above; polars / Spark / DuckDB adapters; a web UI; a remote
  store; nested or binary column types beyond what Phase 1 lists.
- **Delivery.** One pull request per phase, several commits each. The store format carries a version
  from its first commit.
- **Phase order.** Phases 0 to 7 in the order listed.
- **Sign-off.** Each phase lists what the owner confirms before its code is written.

### Status

| Phase | Status | Pull request |
|---|---|---|
| 0 — Light's Hammer: foundation and guidance | Not started | |
| 1 — Frostmourne: soul capture and the Frozen Throne | Not started | |
| 2 — Gunship Battle: sources and the command | Not started | |
| 3 — Lord Marrowgar: schema diff | Not started | |
| 4 — Blood Prince Council: row and value diff | Not started | |
| 5 — Deathbringer Saurfang: the gate | Not started | |
| 6 — Lady Deathwhisper: reports | Not started | |
| 7 — The Lich King: suite and release | Not started | |

### Running a phase

One development session per phase, in order. A phase starts only when the previous phase's pull request
is merged. Kick-off prompt: "Implement Phase N of `ROADMAP.md` following its Running a phase section."

1. **Read.** This file, then (from Phase 1 on) `CLAUDE.md` and the skill; route each commit through the
   skill's workflow file.
2. **Sign-off first.** A sign-off item with a *proposed* default is already accepted (owner, 2026-11-25) and
   is not asked again. Present the remaining items — those with no default, and the concrete form of the
   accepted ones (signatures, file layouts with sample content, sample output) — to the owner and wait for
   confirmation before writing code. Record each confirmed decision under the phase, dated, in the phase's
   first commit.
3. **Implement.** One commit per table row, in order, each passing `python tools/verify.py` (from the
   commit of Phase 0 that creates it).
4. **Review.** The `reviewer` agent reviews the whole phase diff before the pull request opens; its
   findings are fixed in further commits and reviewed again.
5. **Deliver.** One pull request for the phase; the phase's Status row names it ("In review"). The next
   phase's first commit sets the previous row to "Merged". Each phase adds its entry to one
   "v0.1.0 — in development" section at the top of `RELEASE_NOTES.md`; Phase 7 turns it into the release
   entry and removes the v0.1 section from this file.
6. **Stay in scope.** The scope rules bind every phase. A phase that finds an agreed item infeasible, or
   needs something not listed here, stops and asks the owner; it never narrows or widens scope itself.
7. **Tests are offline.** No test touches the network or a live database; SQL is tested against SQLite
   in memory.

### Phase 0 — Light's Hammer: foundation and guidance

Builds the process every later phase runs under. No product feature.

| Commit | Content |
|---|---|
| 1 | Packaging: `pyproject.toml` (the single product version, `0.1.0.dev0`), the `icecrown/` package skeleton with `__version__` read from the package metadata, `tests/`, `.gitignore`, `.editorconfig`, a dev container, `tools/setup_dev_env.py` (editable install with the dev extra, git hooks). |
| 2 | Operating contract `CLAUDE.md`: operating principles, hard rules (short form, each pointing at its full form), the ask-first list, the workflow for any change. Budget: at most 80 lines and 8 KiB. |
| 3 | Routing skill `.claude/skills/project-icecrown-development/`: `SKILL.md` is a routing table only (task → the one file holding its detail); `references/` holds `conventions.md` (hard rules in full, module layout, simplicity audit, error handling), `style.md` (comments, console messages, CLI flags), `architecture.md` (module map, codenames, data flow), `domain.md` (fingerprint and store concepts), `qa-and-ci.md` (gates, verify, workflows), `checkers.md` (what each guard parses), `recipes.md` (grep-before-coding, decision format, orchestration, lessons loop) and `references/workflows/` (`adding-a-source.md`, `changing-the-fingerprint.md`, `changing-the-store-format.md`, `adding-a-cli-command.md`, `changing-guidance.md`, `releasing.md`). |
| 4 | Agents `.claude/agents/`: `implementer` (writer, from a complete brief; Read, Grep, Glob, Edit, Write, Bash), `reader` (read-only, reads spanning more than three files, answers with `file:line`; Read, Grep, Glob), `reviewer` (independent diff review, never the author, never edits; Read, Grep, Glob, Bash), `scribe` (notes outside the repository tree, never committed; Read, Write). Model and effort live only in agent frontmatter and the roles table of `recipes.md`. |
| 5 | Path rules `.claude/rules/` (pointer-only, at most 6 non-blank body lines, one per guarded area) and command skills (pointer-only): `verify`, `review-diff`, `guidance-change`, `new-source`, `release`. |
| 6 | `.claude/settings.json` (default mode, allow-list for the verify and check commands, `ask` gates mirroring the ask-first list, `deny` for secret files and the built-in explore agent) and hooks: `session-start.sh` (dev tools and git hooks in cloud sessions, skipped by `ICECROWN_SKIP_DEV_SETUP=1`) and `post_edit_check.py` (lint after an edit). |
| 7 | Checkers under `tools/`, each with tests: `check_conventions.py` (the mechanical code conventions), `check_guidance_integrity.py` (pointers and anchors resolve, the `CLAUDE.md` budget, one routing row per reference, rule and command-skill shape), `check_docs_sync.py` (a code change in a documented area touches its doc; `[skip-docs]` on its own line in a commit body is the escape hatch), and `verify.py` (every check plus `ruff check .` and `pytest -q`, one pass/fail table). |
| 8 | `.pre-commit-config.yaml` (conventions, ruff, guidance integrity, gitleaks at pre-commit; docs-sync at commit-msg; fast pytest at pre-push), `.gitleaks.toml`, and CI: `ci-pre-commit`, `ci-docs-sync`, `ci-tests` (pytest with coverage on Linux, macOS and Windows, advisory mypy, gating actionlint, ending in one `CI gate` check), `dependabot.yml`, `CODEOWNERS`. |
| 9 | Community and release docs: `README.md` (what it is, codenames, quick start placeholder, documentation layers), `CONTRIBUTING.md`, `SECURITY.md`, `.github/pull_request_template.md`, `RELEASE_NOTES.md` with the "v0.1.0 — in development" section, `tests/README.md`, `evals/evals.json` (routing and ask-first prompts run by hand before a guidance change merges). |

Design the phase follows:

- **Every fact lives in one file.** `CLAUDE.md` holds the contract; the skill routes each task to its
  authoritative file; module detail lives in that module's `README.md`. A pointer replaces a second copy.
- **Operating principles (proposed).** (1) Flag uncertainties — ask, don't assume; validate a request
  against repository patterns and flag a conflict instead of silently complying. (2) The orchestrator
  designs and signs off; the writer implements; the reader reads; the reviewer reviews. The session owns
  ask-first gates, design, briefs and the done gate (it reads the diff and runs the verify itself); a
  small edit — one file, about 20 changed lines, no ask-first item, no new logic — it makes itself.
  (3) Be concise; never drop a confidence label on an architectural call, a pattern-conflict flag or a
  better approach when one exists. (4) Modular, single source of truth; surgical changes over sweeping
  refactors.
- **Hard rules (proposed set, R1–R8).** R1 registries (sources, codenames, format versions) are imported,
  never hardcoded. R2 shared helpers are reused, never re-implemented; console output goes through the
  shared message helpers. R3 nothing non-deterministic in a fingerprint path. R4 no files the user didn't
  ask for; `tests/` is the only test location. R5 the core is offline and tests are offline. R6 a store
  or fingerprint format change bumps the format version and ships its migration and compatibility test.
  R7 docs move with the code. R8 entry points (CLI commands, the pytest plugin) hold only their flow;
  logic lives in private `_*.py` engine files behind a facade.
- **Ask first (proposed list).** Fingerprint canonicalisation and hash; the store layout and manifest
  format; default tolerances and exit codes; public API and CLI signatures; a new runtime dependency;
  publishing a release; and the guidance machinery and CI (`CLAUDE.md`, `.claude/settings.json`,
  `.claude/agents/`, `.claude/hooks/`, `.github/workflows/`, `.pre-commit-config.yaml`, `.gitleaks.toml`).
- **Workflow for any change.** Understand the request → route through the skill and read the routed file
  → grep the established pattern → validate, flag conflicts → implement → verify → update the changed
  area's docs → simplicity audit and the `reviewer` agent on every non-trivial diff.
- **Subagent briefs** are self-contained: goal, files, exact change, constraints, acceptance criteria,
  report. A reviewer brief gives the diff range and the acceptance criteria, never the author's reasoning.
- **Lessons loop.** A class of review finding becomes, in order of preference, a checker rule, a test, a
  hook, or one guidance line; the pull-request template has a section for it.
- **Pull-request template sections.** Summary; Changes; Docs updated; QA gates run; Review agents run;
  Not tested / to do by hand; Lessons; Format changes (store or fingerprint version bumped? y / n);
  Ask-first items touched.
- **Commits.** Imperative subject, at most 72 characters; the body explains why when it is not obvious.
- **Versioning.** Semantic; the version lives only in `pyproject.toml`; `RELEASE_NOTES.md` is the one
  changelog, newest first.

Sign-off: the hard-rule set and the ask-first list; the agents' model and effort tiers and the session
model named in `.claude/settings.json`; the `permissions` lists; the conventions the checker enforces
mechanically; the CI matrix (operating systems, Python versions); the package name on PyPI (`icecrown`
may be taken — fallback *proposed*: `project-icecrown`, import name `icecrown`); the layout
(`icecrown/` flat package *proposed*, not `src/`).

### Phase 1 — Frostmourne: soul capture and the Frozen Throne

The lead feature. After this phase the Python API can freeze a DataFrame and say whether another one matches.

| Commit | Content |
|---|---|
| 1 | Canonicalisation: one canonical byte form per cell for the supported types (integer, float, boolean, string, date, timestamp, decimal, null), independent of platform and library version. |
| 2 | Row hashes and the content fingerprint: one hash per row; the dataset fingerprint is order-insensitive by default and order-sensitive on request. |
| 3 | Schema fingerprint: column names, canonical types, nullability observed. |
| 4 | The soul: the manifest object (format version, name, schema, row count, schema and content fingerprints, capture options) with a stable JSON form. |
| 5 | The Frozen Throne: `.icecrown/` layout, writing and reading manifests, the accepted-baseline pointer per snapshot name, atomic writes. |
| 6 | Optional frozen copy: a content-addressed Parquet file beside the manifest, written only on request. |
| 7 | Public API: `freeze(df, name, …)`, `matches(df, name, …)`, `Soul`; the Frostmourne banner helper. |
| 8 | Cross-platform golden suite: fixed datasets whose fingerprints are pinned in the tests and must hold on every CI operating system and supported pandas / pyarrow version. |
| 9 | Docs and release-notes entry. |

Sign-off: the hash function (*proposed*: BLAKE2b-256 from the standard library); float handling
(*proposed*: exact IEEE-754 bits by default with `-0.0` and NaN made canonical, and an opt-in `round=`
to N significant digits); string normalisation (*proposed*: none — bytes as stored, UTF-8);
timestamp handling (*proposed*: converted to UTC, naive kept naive and flagged in the schema);
whether column order is part of the schema fingerprint (*proposed*: recorded, but not part of the hash
unless asked); the order-insensitive combination of row hashes; the manifest's JSON layout with a sample
file; the `.icecrown/` directory layout; the signatures of `freeze` and `matches`; which column types
are refused with a clear error in v0.1 (nested, binary, categorical handling).

Agreed design (proposed):

- A soul never holds cell values. Row hashes are kept in the frozen copy only, not in the manifest.
- Manifests are small text files meant to be committed to the user's repository; frozen copies are meant
  to be ignored or stored elsewhere. The layout keeps the two apart so one `.gitignore` line does it.
- The fingerprint depends on the data and the capture options only — not on the file it came from, the
  pandas index, the capture time or the machine.
- A capture option that changes the fingerprint (rounding, order sensitivity, key columns) is recorded in
  the manifest, and `matches` uses the baseline's recorded options, never the caller's defaults.

### Phase 2 — Gunship Battle: sources and the command

| Commit | Content |
|---|---|
| 1 | Source registry and the adapter contract: a source turns a reference into a typed table. |
| 2 | File sources: CSV (explicit dtype handling, no silent inference drift) and Parquet. |
| 3 | SQL source behind the optional extra: a query or table over a user-supplied SQLAlchemy URL or engine; tested on in-memory SQLite. |
| 4 | The `icecrown` command: `freeze`, `status`, `log` over the sources; shared flags; banners; exit codes for usage errors. |
| 5 | Docs and release-notes entry. |

Sign-off: the adapter contract; how a source is written on the command line (*proposed*: a path, or
`sql:<query>` with `--url` / the `ICECROWN_DB_URL` environment variable); CSV type rules; the command
and flag names; the CLI library (*proposed*: `argparse`, no new dependency); that a database URL is
never written to a manifest or a log.

### Phase 3 — Lord Marrowgar: schema diff

| Commit | Content |
|---|---|
| 1 | Schema comparison of two souls: columns added, removed, renamed candidates, retyped, reordered, nullability changed. |
| 2 | The finding model shared by every diff (kind, severity, column, before, after). |
| 3 | `icecrown diff --schema` and the API `diff_schema`. |
| 4 | Docs and release-notes entry. |

Sign-off: the finding model's fields; which schema changes are breaking by default (*proposed*: removed
and retyped columns break; added and reordered columns warn); whether rename detection ships in v0.1
(*proposed*: no — a rename reads as one removed and one added column).

### Phase 4 — Blood Prince Council: row and value diff

| Commit | Content |
|---|---|
| 1 | Keyed reconciliation of the current data against a frozen copy: rows added, removed, changed; duplicate-key detection. |
| 2 | Value diff per changed row and column, with absolute and relative tolerances declared per column. |
| 3 | Summary statistics of a diff: counts per kind and per column, the largest moves. |
| 4 | Keyless fallback: when no key is declared, the diff reports row-hash multiset differences only. |
| 5 | `icecrown diff` and the API `diff`; memory bounds documented and tested on a large synthetic table. |
| 6 | Docs and release-notes entry. |

Sign-off: how keys and tolerances are declared; tolerance semantics (*proposed*: a value passes when it
is within the absolute *or* the relative tolerance; NaN equals NaN; null differs from zero); what a diff
does without a frozen copy (*proposed*: it reports that only match / no-match is available and names the
freeze option); the size it must handle in memory (*proposed*: 5 million rows × 50 columns on 8 GB).

### Phase 5 — Deathbringer Saurfang: the gate

| Commit | Content |
|---|---|
| 1 | `icecrown verify`: recompute, compare against the accepted baseline, exit non-zero on a breaking finding. |
| 2 | `icecrown accept`: make the current state the baseline, with a required reason kept in the snapshot's history. |
| 3 | The pytest plugin: an `icecrown` fixture (`icecrown.check(df, name)`) and an `--icecrown-accept` flag. |
| 4 | A documented GitHub Actions example that runs `verify` on a pull request. |
| 5 | Docs and release-notes entry. |

Sign-off: the exit-code table (*proposed*: 0 match, 1 drift, 2 usage or configuration error, 3 missing
baseline); behaviour on a first run with no baseline (*proposed*: fail, and say how to freeze); the
fixture's name and signature; what the history records (reason, previous and new fingerprint, version —
*proposed*: no user name, no timestamp inside the fingerprinted manifest).

### Phase 6 — Lady Deathwhisper: reports

| Commit | Content |
|---|---|
| 1 | The report model: one structure built from the findings of Phases 3 to 5. |
| 2 | Console report: summary first, then schema findings, then the largest value moves, bounded in length. |
| 3 | Markdown report sized for a pull-request comment, and a JSON report with a versioned schema. |
| 4 | `--report` / `--format` flags on `verify` and `diff`. |
| 5 | Docs and release-notes entry. |

Sign-off: the three layouts with sample output; whether a report may show cell values (*proposed*: yes
in the console, off by default in Markdown and JSON, behind `--show-values`); the length bounds.

### Phase 7 — The Lich King: suite and release

| Commit | Content |
|---|---|
| 1 | `icecrown.toml`: every snapshot of a project declared once (name, source, keys, tolerances, options). |
| 2 | `icecrown verify` and `icecrown freeze` with no argument run the whole suite; one combined report and exit code. |
| 3 | An end-to-end example project under `examples/`, exercised by a test. |
| 4 | Documentation pass: README quick start, the user guide, the store-format reference. |
| 5 | Release: the v0.1.0 entry in `RELEASE_NOTES.md`, version `0.1.0`, the v0.1 section removed from this file, the tag and the PyPI publish workflow. |

Sign-off: the `icecrown.toml` schema with a sample file; the publish route (*proposed*: PyPI trusted
publishing from a tag-triggered workflow); the go / no-go for publishing v0.1.0 — a public release is
never made without the owner's explicit confirmation.

### After v0.1

Not planned in detail. Candidates, in no agreed order, each a codename from the table above: Valithria
Dreamwalker (`thaw`), Festergut and Rotface (drift and rot checks that need no row-level baseline),
Blood-Queen Lana'thel (lineage), Professor Putricide (fault injection), Sindragosa (retention and a
remote store), and further Gunship sources (polars, DuckDB). The owner picks the v0.2 scope when v0.1
is tagged.
