# Recipes

How work is done here: finding the pattern, asking for a decision, sharing work between agents, and
learning from review findings.

## Grep before coding

Before writing anything new, look for what exists:

1. The registry or helper that already covers it (`rg "def <verb>" src/`, `rg "<concept>" src/`).
2. The established pattern for the same kind of change (`git log --oneline -- <area>`; the
   [workflows](../SKILL.md)).
3. The test that pins the behaviour you are about to change.

If the pattern conflicts with the request, flag it; do not silently pick one.

## Decision format

Ask the owner one decision at a time, in this shape:

- **Question** — one sentence.
- **Options** — two to four, each with its consequence.
- **Recommendation** — the option, with a confidence label: *high* (verified in code or docs),
  *medium* (reasoned, not verified), *low* (a judgement call).
- **What changes if accepted** — files, formats, versions.

A confirmed decision is recorded, dated, in the commit that applies it (for a phase sign-off, under
the phase in `ROADMAP.md`).

## Roles

Model and effort live only here and in each agent's frontmatter; checker G6 keeps the two equal.

| Role | Agent | Model | Effort | Tools | Use it for |
|---|---|---|---|---|---|
| Orchestrator | the session | `opus` | `high` | all | Design, sign-off, briefs, ask-first gates, the done gate |
| Writer | `implementer` | `opus` | `high` | Read, Grep, Glob, Edit, Write, Bash | Implementing a complete brief |
| Reader | `reader` | `sonnet` | `medium` | Read, Grep, Glob | A read spanning more than three files; answers with `file:line` |
| Reviewer | `reviewer` | `opus` | `xhigh` | Read, Grep, Glob, Bash | An independent review of a diff; never the author, never edits |
| Scribe | `scribe` | `haiku` | `low` | Read, Write | Notes outside the repository tree, never committed |

The session's model and effort are set in `.claude/settings.json`.

## Briefs

A brief is self-contained; the agent knows nothing else.

- **Goal** — the outcome, in one or two sentences.
- **Files** — the files to read and the files to change.
- **Exact change** — what to add, remove or rename.
- **Constraints** — the hard rules and ask-first items that apply; what not to touch.
- **Acceptance criteria** — checkable statements, including `uv run python tools/verify.py` passing.
- **Report** — what to send back: the diff summary, the verify table, open questions.

A reviewer brief gives the diff range (`git diff <base>..<head>`) and the acceptance criteria —
never the author's reasoning, so the review is not anchored on it.

## Orchestration

- Independent reads and reviews run in parallel; writes to the same files never do.
- The session reads every diff an agent produces and runs the verify command itself before it calls
  the work done.
- The `reviewer` reviews the whole phase diff before a pull request opens; its findings are fixed in
  further commits and reviewed again.

## Lessons loop

A class of review finding (not a one-off) becomes, in order of preference:

1. a checker rule ([checkers.md](checkers.md));
2. a test;
3. a hook;
4. one line of guidance, in the one file that owns the topic.

The pull-request template's *Lessons* section records which one was chosen.
