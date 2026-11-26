"""The guidance-integrity checker, G1 to G7, on small synthetic trees."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import check_guidance_integrity as gi
from _toolkit import repo_root

if TYPE_CHECKING:
    from pathlib import Path

SKILL = ".claude/skills/project-icecrown-development"
ROLES = """# Recipes

## Roles

| Role | Agent | Model | Effort | Tools |
|---|---|---|---|---|
| Orchestrator | the session | `opus` | `high` | all |
| Writer | `implementer` | `opus` | `high` | Edit |
"""
AGENT = (
    "---\nname: implementer\ndescription: d\ntools: Read\nmodel: opus\neffort: high\n---\n\nBody\n"
)


def make_tree(tmp_path: Path, files: dict[str, str] | None = None) -> Path:
    base = {
        "CLAUDE.md": f"# Contract\n\nSee [the skill]({SKILL}/SKILL.md).\n",
        f"{SKILL}/SKILL.md": (
            "---\nname: x\ndescription: y\n---\n\n| Task | Read |\n|---|---|\n"
            "| Recipes | [recipes.md](references/recipes.md) |\n"
        ),
        f"{SKILL}/references/recipes.md": ROLES,
        ".claude/agents/implementer.md": AGENT,
        ".claude/settings.json": json.dumps({"model": "opus", "effortLevel": "high"}),
    }
    for rel, text in {**base, **(files or {})}.items():
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return tmp_path


def codes(root: Path) -> list[str]:
    return [f"{v.code}:{v.path}" for v in gi.check(root)]


def test_clean_tree_passes(tmp_path: Path) -> None:
    assert gi.check(make_tree(tmp_path)) == []


def test_g1_broken_links_anchors_and_escapes(tmp_path: Path) -> None:
    root = make_tree(
        tmp_path,
        {
            "README.md": (
                "# Readme\n[ok](CLAUDE.md#contract) [self](#readme) [web](https://example.com)\n"
                "[gone](missing.md) [anchor](CLAUDE.md#nope) [out](../outside.md)\n"
            )
        },
    )
    messages = sorted(v.message for v in gi.check(root))
    assert messages == [
        "broken link: missing.md",
        "link leaves the repository: ../outside.md",
        "missing anchor: CLAUDE.md#nope",
    ]


def test_g2_contract_budget(tmp_path: Path) -> None:
    root = make_tree(tmp_path, {"CLAUDE.md": "line\n" * (gi.CONTRACT_MAX_LINES + 1)})
    assert codes(root) == ["G2:CLAUDE.md"]


def test_g2_missing_contract(tmp_path: Path) -> None:
    root = make_tree(tmp_path)
    (root / "CLAUDE.md").unlink()
    assert codes(root) == ["G2:CLAUDE.md"]


def test_g3_every_reference_has_exactly_one_row(tmp_path: Path) -> None:
    root = make_tree(
        tmp_path,
        {
            f"{SKILL}/references/workflows/unrouted.md": "# Unrouted\n",
            f"{SKILL}/SKILL.md": (
                "| Task | Read |\n|---|---|\n| A | [r](references/recipes.md) |\n"
                "| B | [r](references/recipes.md#roles) |\n"
            ),
        },
    )
    messages = sorted(v.message for v in gi.check(root) if v.code == "G3")
    assert messages == [
        "no routing row for references/workflows/unrouted.md",
        "references/recipes.md is routed by 2 rows",
    ]


def test_g4_rules_need_paths_and_pointer_only_bodies(tmp_path: Path) -> None:
    root = make_tree(
        tmp_path,
        {
            ".claude/rules/good.md": (
                '---\npaths:\n  - "src/**"\n---\n\nSee [x](../../CLAUDE.md).\n'
            ),
            ".claude/rules/bad.md": "---\nname: x\n---\n\nNo link here.\n"
            + "[l](../../CLAUDE.md)\n" * 6,
        },
    )
    messages = sorted(v.message for v in gi.check(root) if v.code == "G4")
    assert messages == [
        "7 body lines (at most 6, pointer-only)",
        "body line holds no link (pointer-only)",
        "frontmatter needs a non-empty 'paths' list",
    ]


def test_g5_command_skills(tmp_path: Path) -> None:
    root = make_tree(
        tmp_path,
        {".claude/skills/verify/SKILL.md": "---\nname: verify\n---\n\nJust text.\n"},
    )
    messages = sorted(v.message for v in gi.check(root) if v.code == "G5")
    assert messages == ["body line holds no link (pointer-only)", "frontmatter needs 'description'"]


def test_g6_agents_match_the_roles_table(tmp_path: Path) -> None:
    root = make_tree(
        tmp_path,
        {
            ".claude/agents/implementer.md": AGENT.replace("effort: high", "effort: low"),
            ".claude/agents/stray.md": "---\nname: stray\n---\n",
            ".claude/settings.json": json.dumps({"model": "sonnet", "effortLevel": "high"}),
        },
    )
    messages = sorted(v.message for v in gi.check(root) if v.code == "G6")
    assert messages == [
        "'stray' has no row in the roles table",
        "effort 'low'; the roles table says 'high'",
        "frontmatter needs 'description'",
        "frontmatter needs 'effort'",
        "frontmatter needs 'model'",
        "frontmatter needs 'tools'",
        "model 'sonnet'; the roles table says 'opus'",
    ]


def test_g6_roles_without_an_agent_file(tmp_path: Path) -> None:
    root = make_tree(tmp_path)
    (root / ".claude/agents/implementer.md").unlink()
    assert [v.message for v in gi.check(root)] == [
        "roles table names 'implementer', which has no agent file"
    ]


def test_g7_evals(tmp_path: Path) -> None:
    evals = {
        "evals": [
            {"id": "a", "prompt": "p", "expect": "references/recipes.md"},
            {"id": "b", "prompt": "p", "expect": "ask-first: publishing"},
            {"id": "a", "prompt": "p", "expect": "references/nowhere.md"},
            {"id": "c", "prompt": "p"},
        ]
    }
    root = make_tree(tmp_path, {"evals/evals.json": json.dumps(evals)})
    messages = sorted(v.message for v in gi.check(root))
    assert messages == [
        "a: unknown route 'references/nowhere.md'",
        "duplicate eval id 'a'",
        "eval #3 needs string id, prompt, expect",
    ]


def test_g7_invalid_json_and_shape(tmp_path: Path) -> None:
    assert codes(make_tree(tmp_path, {"evals/evals.json": "{"})) == ["G7:evals/evals.json"]
    assert codes(make_tree(tmp_path, {"evals/evals.json": "[]"})) == ["G7:evals/evals.json"]


def test_the_repository_itself_passes() -> None:
    assert gi.check(repo_root()) == []
