# Project Icecrown

**Snapshot testing for tabular data.** Freeze the output of a data pipeline, verify it on every run or
pull request, and see exactly which rows, columns and values moved when it changed.

> **Status: in development.** No product feature has shipped yet. The scope, the build order and
> each phase's status are in [`ROADMAP.md`](https://github.com/Deluha/icecrown/blob/main/ROADMAP.md).

## What it does

Unit tests cover code, not data. A refactor that "changes nothing" can still shift a rating, drop forty
rows or turn a column from integer to float. Icecrown gives a pipeline the safety net a UI gets from
snapshot tests:

1. **Freeze** a dataset: capture a deterministic fingerprint (and optionally a frozen copy) as the
   baseline.
2. **Verify** on every run or pull request: recompute the fingerprint and compare.
3. **Explain** a mismatch: schema diff, keyed row diff, value diff within declared tolerances.
4. **Accept** an intended change explicitly; the commit that changes the baseline file is the record.

The baseline is a small, hash-only text file committed next to the code — no cell values — and the same
data gives the same fingerprint whether it arrives as an Arrow table, a pandas DataFrame, a CSV, a
Parquet file or a SQL result. The fingerprint is a published specification with test vectors. A Python
library, an `icecrown` command and a pytest plugin; no server, no account, no network access.

## Quick start

Coming with the first features (Phases 1 and 2 of the roadmap). Installation will be:

```bash
pip install icecrown
```

## Codenames

Each system is named after Icecrown Citadel. **Frostmourne**, the lead feature, is the snapshot engine:
it captures a dataset's *soul* — a deterministic fingerprint of its schema and content — and keeps it in
the Frozen Throne, the snapshot store. The full table is in the [roadmap](https://github.com/Deluha/icecrown/blob/main/ROADMAP.md#codenames). The
codenames appear in a banner on an interactive terminal only; logs and CI output stay plain.

## Documentation

| For | Read |
|---|---|
| Users | The documentation site, built from [`docs/`](https://github.com/Deluha/icecrown/blob/main/docs/index.md): user guide, [compatibility promise](https://github.com/Deluha/icecrown/blob/main/docs/compatibility.md), fingerprint spec and store format |
| Contributors | [CONTRIBUTING.md](https://github.com/Deluha/icecrown/blob/main/CONTRIBUTING.md): one command, `uv run python tools/verify.py`, runs the checkers, lint, types and tests |
| AI agents | [CLAUDE.md](https://github.com/Deluha/icecrown/blob/main/CLAUDE.md), the operating contract, and the development skill it routes through |
| What changed | `CHANGELOG.md`; what is planned: [ROADMAP.md](https://github.com/Deluha/icecrown/blob/main/ROADMAP.md) |

Security issues: see [SECURITY.md](https://github.com/Deluha/icecrown/blob/main/SECURITY.md). Everyone taking part follows the
[code of conduct](https://github.com/Deluha/icecrown/blob/main/CODE_OF_CONDUCT.md).

## License

[MIT](https://github.com/Deluha/icecrown/blob/main/LICENSE).

## Name

Project Icecrown is an independent open source project, named after the legendary raid as an homage. It is
not affiliated with or endorsed by Blizzard Entertainment, and it has nothing to do with World of Warcraft.
