---
name: project-icecrown-development
description: Routing table for every change to Project Icecrown — code, tests, docs, CI, guidance or a release. Read it first on any task; each row names the one file that holds the detail.
---

# Project Icecrown development

Find the task's row, read the one file it names, and follow it. Each file is the only home of its
facts. Product facts — the fingerprint spec, the store format, the user guide — live under `docs/`,
and these files point there.

| Task | Read |
|---|---|
| Any code change: the hard rules in full, the ask-first list, module layout, errors, the simplicity audit | [conventions.md](references/conventions.md) |
| Docstrings, comments, console messages, CLI flags, banners, prose, commit messages | [style.md](references/style.md) |
| Where something lives: module map, codenames, data flow, format versions | [architecture.md](references/architecture.md) |
| Running the gates: the verify command, tests, coverage, CI workflows, hooks, the support matrix | [qa-and-ci.md](references/qa-and-ci.md) |
| What a checker enforces, or why one failed | [checkers.md](references/checkers.md) |
| Grep before coding, asking for a decision, roles, briefs, orchestration, the lessons loop | [recipes.md](references/recipes.md) |
| Adding a source adapter | [adding-a-source.md](references/workflows/adding-a-source.md) |
| Changing how a fingerprint is computed | [changing-the-fingerprint.md](references/workflows/changing-the-fingerprint.md) |
| Changing the store layout or the baseline-file format | [changing-the-store-format.md](references/workflows/changing-the-store-format.md) |
| Adding or changing a CLI command | [adding-a-cli-command.md](references/workflows/adding-a-cli-command.md) |
| Changing guidance: `CLAUDE.md`, `.claude/`, `evals/` | [changing-guidance.md](references/workflows/changing-guidance.md) |
| Preparing or publishing a release | [releasing.md](references/workflows/releasing.md) |
