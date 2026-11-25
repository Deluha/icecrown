# Project Icecrown — Roadmap

The planned scope of the next release. `CHANGELOG.md` records what shipped; this file records what is
planned. A release's section leaves this file when the release is tagged. Owner decisions are dated.

Two marks show how firm a value is:

- *proposed* — a default the owner accepted on 2026-11-25. A phase may bring it back to the owner with a
  reason; it never changes one on its own.
- *revised* — changed or added by the independent review of 2026-11-25 (library engineering and technical
  design). **Not yet confirmed by the owner.** A phase asks about its *revised* items at sign-off unless
  the owner has confirmed them before.

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
4. **Accept** an intended change explicitly, so the new state becomes the baseline; the commit that
   changes the baseline file is the record.

Audience: data engineers and analysts with Arrow, pandas or SQL pipelines who want parity checks in CI
without a data platform. Form: a Python library, an `icecrown` command and a pytest plugin. No server, no
account, no network access.

What sets it apart (*revised*): the baseline is a small, hash-only text file committed next to the code,
and the same data gives the same fingerprint whether it arrives as a DataFrame, a CSV, a Parquet file or
a SQL result. The fingerprint is a published specification with test vectors, so a result can be checked
independently of this library. Phase 0 sign-off includes a short written comparison with the existing
tools (DataFrame comparison libraries, snapshot-testing plugins, database diff tools, validation
frameworks, versioned table formats) to confirm that position before code is written.

### Codenames

Each system is named after Icecrown Citadel. An entry point shows its codename in a banner on an
interactive terminal only; logs, CI output and `--quiet` runs stay plain (*revised*).

| Codename | System | In v0.1 |
|---|---|---|
| **Frostmourne** | **The lead feature.** The snapshot engine: it captures a dataset's *soul* — a canonical, deterministic fingerprint of its schema and content, row by row | Phase 1 |
| **The Frozen Throne** | The snapshot store: the `.icecrown/` directory holding one baseline file per snapshot and optional frozen copies | Phase 1 |
| **Light's Hammer** | The foundation: packaging, the guidance machinery, the checkers, CI and the release pipeline | Phase 0 |
| **Gunship Battle** | Sources: the adapters that carry data in (Arrow, pandas, CSV, Parquet, SQL) and the `icecrown` command itself | Phase 2 |
| **Lord Marrowgar** | The schema ("bones") diff: columns added, removed, reordered, retyped | Phase 3 |
| **Blood Prince Council** | The keyed row and value diff: two datasets reconciled into added, removed and changed rows, within tolerances | Phase 4 |
| **Deathbringer Saurfang** | The gate: `verify` / `accept` with tolerances and the pytest plugin — the thing that fails a build | Phase 5 |
| **Lady Deathwhisper** | Reports: the findings as Markdown (for a pull request) and JSON | Phase 6 |
| **The Lich King** | The suite: the whole project's snapshots run as one, and the release | Phase 7 |
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
- **Quality bar.** A state-of-the-art library that follows current industry best practice.

Accepted as proposed (owner, 2026-11-25):

- **Offline and local.** The core makes no network call and needs no service. A database is reached only
  through a connection the user supplies.
- **Deterministic.** The same data gives the same fingerprint on every machine, operating system and
  library version the release supports. No wall-clock time, randomness or environment-dependent ordering
  enters a fingerprint.
- **Not in v0.1.** The *later* codenames above; polars / Spark / DuckDB adapters; a web UI; a remote
  store; nested column types.
- **Delivery.** One pull request per phase, several commits each.
- **Phase order.** Phases 0 to 7 in the order listed.
- **Sign-off.** Each phase lists what the owner confirms before its code is written.

*Revised* by the review (awaiting owner confirmation):

- **Arrow is the core.** The only runtime dependency is `pyarrow`; the fingerprint is computed from Arrow
  data. pandas is an optional extra and one adapter among others, as is SQL (`sqlalchemy`). This replaces
  the accepted default "`pandas` and `pyarrow`": pandas types change with a single null and between
  pandas versions, which would break the determinism rule. A new runtime dependency stays ask-first.
- **Support policy.** Every Python version that is not end-of-life, from 3.11. A stated lower bound for
  each dependency (`pyarrow` no lower than the release that fixed its known deserialisation
  vulnerability), tested in CI at the lowest bound, the latest release and the next pre-release.
- **Typed.** The package ships `py.typed` and passes a strict type check that gates every pull request.
- **What the privacy claim covers.** A baseline file holds hashes, schema and counts — never cell values —
  and a frozen copy is written only on request. The hashes are unsalted: someone who can guess a row can
  confirm it, so a baseline of low-entropy or very small data is not secret. Row hashes are never printed.
- **Threat model.** The fingerprint detects accidental change. It is not a defence against a party who
  deliberately constructs a colliding dataset.
- **Two format versions.** The store-format version (file layout; migratable) and the fingerprint-spec
  version (how bytes are hashed; an older spec stays readable or gives a clear "freeze again" error) are
  separate, both written from the first commit. Migrations are owed only from the 0.1.0 tag on.
- **Compatibility promise.** What is public (`__all__`, the exception hierarchy, the CLI, the store
  format, the fingerprint spec), what 0.x may break and how a deprecation is announced is written down
  in Phase 0 and published with the release.

### Status

| Phase | Status | Pull request |
|---|---|---|
| 0 — Light's Hammer: foundation and guidance | Not started | |
| 1 — Frostmourne: soul capture and the Frozen Throne | Not started | |
| 2 — Gunship Battle: sources, the command and the basic gate | Not started | |
| 3 — Lord Marrowgar: findings and schema diff | Not started | |
| 4 — Blood Prince Council: row and value diff | Not started | |
| 5 — Deathbringer Saurfang: the full gate | Not started | |
| 6 — Lady Deathwhisper: reports | Not started | |
| 7 — The Lich King: suite and release | Not started | |

### Running a phase

One development session per phase, in order. A phase starts only when the previous phase's pull request
is merged. Kick-off prompt: "Implement Phase N of `ROADMAP.md` following its Running a phase section."

1. **Read.** This file, then (from Phase 1 on) `CLAUDE.md` and the skill; from Phase 1 on, route each
   commit through the skill's workflow file.
2. **Sign-off first.** A sign-off item with a *proposed* default is already accepted and is not asked
   again. Present the remaining items — every *revised* item, those with no default, and the concrete
   form of the accepted ones (signatures, file layouts with sample content, sample output) — to the owner
   and wait for confirmation before writing code. Record each confirmed decision under the phase, dated,
   in the phase's first commit, and drop its *revised* mark.
3. **Implement.** One commit per table row, in order, each passing the verify command (from the commit
   of Phase 0 that creates it).
4. **Review.** The `reviewer` agent reviews the whole phase diff before the pull request opens; its
   findings are fixed in further commits and reviewed again.
5. **Deliver.** One pull request for the phase; the phase's Status row names it ("In review"). The next
   phase's first commit sets the previous row to "Merged". Each phase adds its entry to the
   "Unreleased" section at the top of `CHANGELOG.md`; Phase 7 turns it into the release entry.
6. **Stay in scope.** The scope rules bind every phase. A phase that finds an agreed item infeasible, or
   needs something not listed here, stops and asks the owner; it never narrows or widens scope itself.
7. **Tests are offline.** No test touches the network or a live database.
8. **Each phase ships something usable.** The package builds, installs and passes its tests from the
   built wheel at the end of every phase.

### Phase 0 — Light's Hammer: foundation and guidance

Builds the process and the pipeline every later phase runs under. No product feature.

| Commit | Content |
|---|---|
| 1 | Packaging: `pyproject.toml` with a standards-based build backend, SPDX licence expression, project URLs, the single product version (`0.1.0.dev0`) and dependency groups; `src/icecrown/` skeleton with `py.typed` and `__version__` read from the package metadata; a lockfile for development; `.gitignore`, `.gitattributes` (LF for text), `.editorconfig`; the source distribution excludes `.claude/`, `tools/` and `evals/`. Reserve the name `icecrown` on PyPI (free on 2026-11-25; distribution and import name are the same). |
| 2 | Quality configuration: lint and format (`ruff check`, `ruff format`), strict type check, pytest with warnings as errors, branch coverage with a threshold, property-based testing (Hypothesis), `.pre-commit-config.yaml` with the lint, format, type and secret-scan hooks, `.gitleaks.toml`. |
| 3 | Operating contract `CLAUDE.md`: operating principles, hard rules (short form, each pointing at its full form), the ask-first list, the workflow for any change. Budget: at most 80 lines and 8 KiB. |
| 4 | Routing skill `.claude/skills/project-icecrown-development/`: `SKILL.md` is a routing table only (task → the one file holding its detail); `references/` holds `conventions.md` (hard rules in full, module layout, simplicity audit, error handling), `style.md` (comments, console messages, CLI flags), `architecture.md` (module map, codenames, data flow), `qa-and-ci.md` (gates, verify, workflows), `checkers.md` (what each guard parses), `recipes.md` (grep-before-coding, decision format, orchestration, lessons loop) and `references/workflows/` (`adding-a-source.md`, `changing-the-fingerprint.md`, `changing-the-store-format.md`, `adding-a-cli-command.md`, `changing-guidance.md`, `releasing.md`). Product facts (fingerprint spec, store format, user guide) live once, under `docs/`; the skill points there. |
| 5 | Agents `.claude/agents/`: `implementer` (writer, from a complete brief; Read, Grep, Glob, Edit, Write, Bash), `reader` (read-only, reads spanning more than three files, answers with `file:line`; Read, Grep, Glob), `reviewer` (independent diff review, never the author, never edits; Read, Grep, Glob, Bash), `scribe` (notes outside the repository tree, never committed; Read, Write). Model and effort live only in agent frontmatter and the roles table of `recipes.md`. |
| 6 | Path rules `.claude/rules/` (pointer-only, at most 6 non-blank body lines, one per guarded area) and command skills (pointer-only): `verify`, `review-diff`, `guidance-change`, `new-source`, `release`. |
| 7 | `.claude/settings.json` (default mode, allow-list for the verify and check commands, `ask` gates mirroring the ask-first list, `deny` for secret files and the built-in explore agent) and hooks: `session-start.sh` (dev environment and git hooks in cloud sessions, skipped by `ICECROWN_SKIP_DEV_SETUP=1`) and `post_edit_check.py` (lint after an edit). |
| 8 | Checkers under `tools/`, their tests under `tests/tools/`: `check_conventions.py` (the mechanical code conventions), `check_guidance_integrity.py` (pointers and anchors resolve, the `CLAUDE.md` budget, one routing row per reference, rule and command-skill shape), `check_docs_sync.py` (a code change in a documented area touches its doc; `[skip-docs]` on its own line in a commit body is the escape hatch), and `verify.py` (every check plus lint, format check, type check and tests; one pass/fail table). The checker hooks join the pre-commit config (docs-sync at commit-msg). |
| 9 | CI: `ci-pre-commit`, `ci-docs-sync`, `ci-tests` (the support-policy matrix on Linux, macOS and Windows, including one arm64 runner; lowest-bound, latest and pre-release dependency jobs; coverage; ending in one `CI gate` check) and `ci-build` (source distribution and wheel built on every pull request, metadata checked, the test suite run against the installed wheel). |
| 10 | Supply chain: every action pinned to a commit hash, least-privilege token permissions at the top of each workflow, workflow linting (actionlint and a workflow security linter), code scanning, dependency review, an OpenSSF Scorecard workflow, `dependabot.yml`, `CODEOWNERS`, and the branch ruleset the owner applies to `main`. |
| 11 | Release pipeline, rehearsed: a tag-triggered workflow using PyPI trusted publishing with build attestations, behind an approval-gated environment, creating the GitHub Release from the changelog entry. Proven in this phase by publishing `0.1.0.dev0` to TestPyPI. |
| 12 | Documentation site skeleton under `docs/`, built in CI with warnings as errors: home, user guide stub, API reference generated from docstrings, the compatibility promise, placeholders for the fingerprint spec and the store-format reference. |
| 13 | Community and release docs: `README.md` (what it is, codenames, quick start placeholder, documentation layers), `CONTRIBUTING.md` (a contributor needs only the verify command; the agent machinery is optional for humans), `CODE_OF_CONDUCT.md`, `SECURITY.md` (GitHub private vulnerability reporting, supported versions), issue templates, `.github/pull_request_template.md`, `CHANGELOG.md` with the "Unreleased" section, `tests/README.md`, `evals/evals.json` (routing and ask-first prompts run by hand before a guidance change merges). |

Design the phase follows:

- **Every fact lives in one file.** `CLAUDE.md` holds the contract; the skill routes each task to its
  authoritative file; product documentation lives under `docs/`. A pointer replaces a second copy.
- **Operating principles (proposed).** (1) Flag uncertainties — ask, don't assume; validate a request
  against repository patterns and flag a conflict instead of silently complying. (2) The orchestrator
  designs and signs off; the writer implements; the reader reads; the reviewer reviews. The session owns
  ask-first gates, design, briefs and the done gate (it reads the diff and runs the verify itself); a
  small edit — one file, about 20 changed lines, no ask-first item, no new logic — it makes itself.
  (3) Be concise; never drop a confidence label on an architectural call, a pattern-conflict flag or a
  better approach when one exists. (4) Modular, single source of truth; surgical changes over sweeping
  refactors.
- **Hard rules (proposed set, R1–R8; R4 and R6 *revised*).** R1 registries (sources, logical types,
  format versions) are imported, never hardcoded. R2 shared helpers are reused, never re-implemented;
  console output goes through the shared message helpers. R3 nothing non-deterministic in a fingerprint
  path. R4 no files the user didn't ask for; every test lives under `tests/`. R5 the core is offline and
  tests are offline. R6 a store-format or fingerprint-spec change bumps its version, updates the published
  spec and its test vectors, and — from the 0.1.0 tag on — ships a migration or a clear "freeze again"
  error with a compatibility test. R7 docs move with the code. R8 entry points (CLI commands, the pytest
  plugin) hold only their flow; logic lives in private `_*.py` modules, and the public API is what
  `icecrown/__init__.py` exports.
- **Ask first (proposed list).** The fingerprint spec (canonicalisation, hash, combination); the store
  layout and baseline-file format; default tolerances and exit codes; public API and CLI signatures; a
  new runtime dependency or a changed lower bound; publishing a release; and the guidance machinery and
  CI (`CLAUDE.md`, `.claude/settings.json`, `.claude/agents/`, `.claude/hooks/`, `.github/workflows/`,
  `.pre-commit-config.yaml`, `.gitleaks.toml`).
- **Workflow for any change.** Understand the request → route through the skill and read the routed file
  → grep the established pattern → validate, flag conflicts → implement → verify → update the changed
  area's docs → simplicity audit and the `reviewer` agent on every non-trivial diff.
- **Subagent briefs** are self-contained: goal, files, exact change, constraints, acceptance criteria,
  report. A reviewer brief gives the diff range and the acceptance criteria, never the author's reasoning.
- **Lessons loop.** A class of review finding becomes, in order of preference, a checker rule, a test, a
  hook, or one guidance line; the pull-request template has a section for it.
- **Pull-request template sections.** Summary; Changes; Docs updated; QA gates run; Review agents run;
  Not tested / to do by hand; Lessons; Format changes (store-format or fingerprint-spec version bumped?
  y / n); Ask-first items touched.
- **Commits.** Imperative subject, at most 72 characters; the body explains why when it is not obvious.
- **Versioning.** Semantic; the version lives only in `pyproject.toml`; `CHANGELOG.md` is the one
  changelog, newest first, in the Keep a Changelog layout.

Sign-off: the *revised* scope rules above; the prior-art comparison; the hard-rule set and the ask-first
list; the agents' model and effort tiers and the session model named in `.claude/settings.json`; the
`permissions` lists; the conventions the checker enforces mechanically; the exact CI matrix; the tools
behind commits 1, 2, 10 and 12 (*revised* defaults: `hatchling`, `uv` with `uv.lock`, `ruff`, `mypy`
strict, `zizmor`, CodeQL; the documentation generator is chosen at sign-off after checking which ones
are actively maintained); the coverage threshold (*revised*: 90 % branch); the `src/` layout
(*revised*, replacing the accepted flat layout: tests then run against the installed package, not the
checkout); `CHANGELOG.md` (*revised*, replacing `RELEASE_NOTES.md`); the branch ruleset.

Kept against the review's advice, because they are owner decisions: the full agent process in this phase
(the review found it heavy for a one-maintainer v0.1) and the codenames (the review suggested keeping
them out of user-facing output; the banner rule above is the compromise).

### Phase 1 — Frostmourne: soul capture and the Frozen Throne

The lead feature. After this phase the Python API can freeze a table and say whether another one matches.

| Commit | Content |
|---|---|
| 1 | The fingerprint specification, written before the code (`docs/`): the logical type model, the canonical byte form of each type, the row encoding, the combination of row hashes, and test vectors. Spec version 1. |
| 2 | Logical types on Arrow: integer, float, boolean, string, binary, date, time, timestamp (naive and zone-aware are distinct types), duration, decimal, null. The value is hashed, not its storage width: the same integer hashes the same as int8 or int64; dictionary-encoded columns are decoded. Refused with a clear error: nested types, columns of mixed type, duplicate or non-string column names. |
| 3 | Canonicalisation, vectorised and batched: one canonical byte form per cell, each with a type tag and a length prefix, so no two different rows share an encoding. |
| 4 | Row hashes and the content fingerprint: cells are bound to their column names and hashed in sorted-name order; the order-insensitive fingerprint is the sum of the row hashes modulo 2^256, finalised with the row count and the schema fingerprint, so duplicate rows count; an order-sensitive mode on request. |
| 5 | Schema fingerprint: column names and logical types. Storage width, column order and observed nullability are recorded beside it but are not part of the hash. |
| 6 | The soul: the baseline object (store-format version, spec version, name, schema, row count, schema and content fingerprints, one fingerprint per column, capture options) with a stable JSON form — sorted keys, LF line endings, no timestamp, no user or machine name. |
| 7 | The Frozen Throne: `.icecrown/snapshots/<name>.json`, one file per snapshot, which *is* the accepted baseline; snapshot names validated (no path traversal, safe on case-insensitive and Windows file systems); atomic writes. |
| 8 | Optional frozen copy: a Parquet file under `.icecrown/frozen/`, named by the content fingerprint (not by its file bytes), written only on request, verified against the fingerprint when read. |
| 9 | Public API: `freeze(table, name, …)` and `verify(table, name, …)` returning a result object, `Soul`, the exception hierarchy; the pandas adapter behind the optional extra, which refuses a non-default index unless the caller says whether it is data. |
| 10 | Tests: the spec's test vectors; cross-platform golden fingerprints pinned across the CI matrix; property-based tests (row permutation never changes the fingerprint, a duplicated row always does, the same logical data through numpy-backed pandas, nullable pandas and Arrow gives the same fingerprint, a frozen copy reads back to its own fingerprint). |
| 11 | Benchmark suite (opt-in, not a CI gate) with a recorded throughput baseline. |
| 12 | Docs and changelog entry. |

Sign-off: the hash function (*proposed*: BLAKE2b-256 from the standard library); string normalisation
(*proposed*: none — bytes as stored, UTF-8); float handling (*proposed*: exact IEEE-754 bits with `-0.0`
made canonical); NaN and null (*revised*: one value by default, because pandas cannot tell them apart
in a float column; an option keeps them distinct); rounding (*revised*, replacing "N significant
digits": an opt-in number of decimal places per column, documented as unstable at rounding boundaries —
the recommended route for floats is a frozen copy with tolerances, Phase 4); timestamps (*revised*:
zone-aware values are hashed as UTC instants with the zone recorded in the schema; naive and aware
never match each other; one fixed integer unit); decimals (*revised*: the numeric value is hashed,
the scale is recorded in the schema); column order (*proposed*: recorded, not hashed unless asked);
per-column fingerprints in the baseline file (*revised*: on by default, with an option to leave them
out, since they reveal more about low-cardinality columns); the baseline file's JSON layout with a
sample; the `.icecrown/` layout; the signatures of `freeze` and `verify`; the throughput target
(*revised*: set at sign-off from a short spike, before commit 3 fixes the design).

Agreed design:

- A soul never holds cell values. Row hashes are kept in the frozen copy only, never in the baseline
  file and never in output.
- Baseline files are small text files meant to be committed to the user's repository; frozen copies are
  ignored by default, and committing small ones is a documented, supported choice. The layout keeps the
  two apart so one `.gitignore` line does it.
- The fingerprint depends on the data and the capture options only — not on the file it came from, the
  capture time or the machine.
- A capture option that changes the fingerprint (rounding, order sensitivity, NaN handling, index
  handling) is recorded in the baseline file. `verify` uses the recorded options; an explicit argument
  that conflicts with them is an error, never a silent override.
- `freeze` creates a baseline and refuses to replace an existing one; replacing is `accept` (Phase 5).

### Phase 2 — Gunship Battle: sources, the command and the basic gate

After this phase the command line can freeze and verify at fingerprint level, with exit codes, in CI.

| Commit | Content |
|---|---|
| 1 | Source registry and the adapter contract: a source turns a reference into Arrow record batches with logical types. |
| 2 | File sources: Parquet, and CSV read with pinned parsing options (no implicit null strings, no silent type inference): the schema found at `freeze` is recorded in the baseline and re-applied at `verify`, where a value that no longer fits is a finding. |
| 3 | SQL source behind the optional extra: a table name or a query file, read inside one transaction; the connection URL comes from the `ICECROWN_DB_URL` environment variable only and is never written to a baseline, a log or an error message. An order-sensitive snapshot of a query without a stated order is refused. Tested on in-memory SQLite and on synthetic typed result sets for the types SQLite lacks. |
| 4 | Minimal `icecrown.toml`: each snapshot declared once (name, source, capture options). No secrets. |
| 5 | The `icecrown` command: `freeze`, `verify` (fingerprint match or drift, naming the columns whose fingerprint moved) and `status` (the declared snapshots and whether each has a baseline, without reading any source); shared flags; `--quiet`; banners on a terminal only. |
| 6 | Exit codes, documented and tested. |
| 7 | Docs and changelog entry. |

Sign-off: the adapter contract; the `icecrown.toml` schema with a sample file; CSV parsing options; the
command and flag names; the CLI library (*proposed*: `argparse`, no new dependency); the exit-code table
(*proposed*: 0 match, 1 drift, 2 usage or configuration error, 3 missing baseline; *revised*: 4 when a
source cannot be read, so CI can tell drift from an infrastructure failure); behaviour on a first run
with no baseline (*proposed*: fail, and say how to freeze); *revised*, replacing `sql:<query>` with
`--url`: no inline query and no URL flag, because both end up in shell history, process lists and CI logs.

### Phase 3 — Lord Marrowgar: findings and schema diff

| Commit | Content |
|---|---|
| 1 | The finding model shared by every diff and by `verify` (kind, severity, column, before, after) and its console rendering: summary first, bounded in length. `verify` from Phase 2 moves onto it. |
| 2 | Schema comparison of two souls: columns added, removed, retyped, reordered; storage width and nullability changes reported as information. |
| 3 | `icecrown diff --schema` and the API `diff_schema`. |
| 4 | Docs and changelog entry. |

Sign-off: the finding model's fields; the console layout with sample output; which schema changes are
breaking by default (*proposed*: removed and retyped columns break; added and reordered columns warn);
rename detection (*proposed*: not in v0.1 — a rename reads as one removed and one added column);
*revised*: warnings exit 0 unless `--strict` is given.

### Phase 4 — Blood Prince Council: row and value diff

| Commit | Content |
|---|---|
| 1 | Keyed reconciliation of two tables: rows added, removed, changed. Computed as an Arrow join on key and row hash, so only changed rows are materialised. Duplicate or null keys are an error by default. |
| 2 | Value diff per changed row and column, with absolute and relative tolerances declared per column in `icecrown.toml` (numeric, decimal and timestamp columns). |
| 3 | Summary statistics of a diff: counts per kind and per column, the largest moves. |
| 4 | Keyless fallback: when no key is declared, the diff reports how many rows appeared and disappeared — counts only. |
| 5 | `icecrown diff` in two forms — a snapshot against its frozen copy, and any two sources against each other (for CI: the base branch's output against the pull request's) — and the API `diff`. |
| 6 | A scaled memory test with an assertion in CI, and the full-size case in the opt-in benchmark suite. |
| 7 | Docs and changelog entry. |

Sign-off: how keys and tolerances are declared; tolerance semantics (*proposed*: a value passes when it
is within the absolute *or* the relative tolerance; NaN equals NaN; null differs from zero; *revised*:
the relative tolerance is measured against the baseline value, and infinities are equal only with the
same sign); what a diff does without a frozen copy (*proposed*: it reports that only match / no-match
and the moved columns are available, and names the freeze option and the two-source form); the size it
must handle (*proposed*: 5 million rows × 50 columns on 8 GB — in the benchmark suite, not in CI).

### Phase 5 — Deathbringer Saurfang: the full gate

| Commit | Content |
|---|---|
| 1 | `icecrown verify` with tolerances: an equal fingerprint passes; otherwise, with a frozen copy, the tolerance diff decides; without one, it is drift. |
| 2 | `icecrown accept`: replace an existing baseline with the current state. The change to the baseline file, and the commit message the user writes for it, are the history. |
| 3 | The pytest plugin, registered through the standard entry point: a `frostmourne` fixture (`frostmourne.verify(table)`), a default snapshot name derived from the test id, an `--icecrown-accept` flag, safe under parallel test runs, and a report of baselines no test used. Tested with pytest's own plugin-testing fixture. |
| 4 | A documented GitHub Actions example that runs `verify` on a pull request with a read-only token and writes the result to the job summary; it works on pull requests from forks. |
| 5 | Docs and changelog entry. |

Sign-off: the fixture's name and signature (*revised*: `frostmourne`, replacing `icecrown`, which would
shadow `import icecrown` inside a test module); *revised*, replacing the in-store history with a required
reason: no history file — it would conflict on every merge, and git already records who changed a
baseline, when and why; the `status` and `accept` output.

### Phase 6 — Lady Deathwhisper: reports

| Commit | Content |
|---|---|
| 1 | The report model: one structure built from the findings of Phases 3 to 5. |
| 2 | Markdown report sized for a pull request, with every piece of data-derived text escaped. |
| 3 | JSON report with a versioned, documented schema. |
| 4 | `--format` and `--output` on `verify` and `diff`; the console rendering of Phase 3 stays the default. |
| 5 | Docs and changelog entry. |

Sign-off: the two layouts with sample output; whether a report may show cell values (*proposed*: yes
in the console, off by default in Markdown and JSON, behind `--show-values`); the length bounds.

### Phase 7 — The Lich King: suite and release

| Commit | Content |
|---|---|
| 1 | `icecrown verify`, `freeze` and `accept` with no argument run every snapshot in `icecrown.toml`; one combined report and exit code. |
| 2 | An end-to-end example project under `examples/`, exercised by a test under `tests/`. |
| 3 | Documentation pass on the site: quick start, user guide, the fingerprint spec and store-format reference, the compatibility promise, a comparison with related tools. |
| 4 | Release preparation: the v0.1.0 entry in `CHANGELOG.md`, version `0.1.0`, the Status row of this phase set to "In review". |

Release steps, after the pull request merges, each by or with the owner: tag `v0.1.0` → the release
workflow builds and waits at the approval gate → the owner approves → PyPI publish with attestations and
the GitHub Release. A follow-up commit then removes the v0.1 section from this file.

Sign-off: the combined report's layout; the go / no-go for publishing v0.1.0 — a public release is
never made without the owner's explicit confirmation.

### After v0.1

Not planned in detail. Candidates, in no agreed order, each a codename from the table above: Valithria
Dreamwalker (`thaw`), Festergut and Rotface (drift and rot checks that need no row-level baseline),
Blood-Queen Lana'thel (lineage), Professor Putricide (fault injection), Sindragosa (retention and a
remote store), and further Gunship sources (polars, DuckDB). The owner picks the v0.2 scope when v0.1
is tagged.
