# Changing guidance

Guidance is `CLAUDE.md`, everything under `.claude/` and `evals/`. Changes to `CLAUDE.md`,
`.claude/settings.json`, `.claude/agents/` and `.claude/hooks/` are ask-first items.

1. **Ask first** for a gated file, in the [decision format](../recipes.md#decision-format).
2. Put each fact in the one file that owns it (the [routing table](../../SKILL.md)); link to it
   from anywhere else.
3. Keep the shapes the guidance checker enforces ([checkers.md](../checkers.md)): the `CLAUDE.md`
   budget, one routing row per reference, pointer-only rules and command skills, agents matching the
   [roles table](../recipes.md#roles).
4. Prefer a mechanical guard over a guidance line ([lessons loop](../recipes.md#lessons-loop)).
5. Run the routing and ask-first prompts in `evals/evals.json` by hand in a fresh session; record the
   result in the pull request.
6. Run [the verify command](../qa-and-ci.md#verify), then the `reviewer`.
