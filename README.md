# Project Icecrown

**Snapshot testing for tabular data.** Freeze the output of a data pipeline, verify it on every run or
pull request, and see exactly which rows, columns and values moved when it changed.

> **Status: planning.** No code has shipped yet. The scope and the build order are in
> [`ROADMAP.md`](ROADMAP.md).

## Codenames

Each system is named after Icecrown Citadel. **Frostmourne**, the lead feature, is the snapshot engine:
it captures a dataset's *soul* — a deterministic fingerprint of its schema and content — and keeps it in
the Frozen Throne, the snapshot store. The full table is in the roadmap.

## License

[MIT](LICENSE).

## Name

Project Icecrown is an independent open source project, named after the legendary raid as an homage. It is
not affiliated with or endorsed by Blizzard Entertainment, and it has nothing to do with World of Warcraft.
