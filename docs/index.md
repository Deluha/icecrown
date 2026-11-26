# Project Icecrown

**Snapshot testing for tabular data.** Freeze the output of a data pipeline, verify it on every run
or pull request, and see exactly which rows, columns and values moved when it changed.

```{note}
Project Icecrown is in development; no feature has shipped yet. The plan is in the repository's
`ROADMAP.md`.
```

The baseline is a small, hash-only text file committed next to the code, and the same data gives the
same fingerprint whether it arrives as a DataFrame, a CSV, a Parquet file or a SQL result.

```{toctree}
:maxdepth: 2

user-guide
compatibility
reference/fingerprint-spec
reference/store-format
reference/api/icecrown/index
```

Project Icecrown is an independent open source project, named after the legendary raid as an
homage. It is not affiliated with or endorsed by Blizzard Entertainment, and it has nothing to do
with World of Warcraft.
