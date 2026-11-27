---
name: review-diff
description: Have the independent reviewer agent review a diff range (default the branch against main), then fix and re-review its findings.
argument-hint: "[diff range]"
---

Brief the `reviewer` agent with the diff range and acceptance criteria only, as in [recipes.md](../project-icecrown-development/references/recipes.md#briefs).
Fix confirmed findings in further commits and review again, per [recipes.md](../project-icecrown-development/references/recipes.md#orchestration).
Turn a class of finding into a guard through the [lessons loop](../project-icecrown-development/references/recipes.md#lessons-loop).
