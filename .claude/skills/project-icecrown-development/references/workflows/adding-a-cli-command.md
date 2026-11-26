# Adding a CLI command

The `icecrown` command is an entry point (R8): it parses arguments, calls private modules, and maps
results to output and exit codes. A new command, flag or exit code is an ask-first item.

1. **Ask first** with the command's usage line, flags and sample output
   ([decision format](../recipes.md#decision-format)).
2. Put the logic in a private module; the command function in `__main__.py` stays within checker
   C4's line budget.
3. Reuse the shared flags and their meaning ([style.md](../style.md#cli-flags)); no flag carries a
   secret.
4. All output goes through `icecrown._messages` (C1); the banner only on an interactive terminal.
5. Test the exit codes and the output shape, including `--quiet`.
6. Document the command under `docs/` and add a changelog entry (R7).
7. Run [the verify command](../qa-and-ci.md#verify), then the `reviewer`.
