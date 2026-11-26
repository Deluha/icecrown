"""Check the integrity of the guidance files: rules G1 to G7.

What each code means is documented in
``.claude/skills/project-icecrown-development/references/checkers.md``.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from _toolkit import (
    Violation,
    heading_slugs,
    iter_links,
    repo_root,
    report,
    split_frontmatter,
    table_rows,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

TOP_LEVEL_GUIDANCE = ("CLAUDE.md", "README.md", "CONTRIBUTING.md", "tests/README.md")
CONTRACT = "CLAUDE.md"
CONTRACT_MAX_LINES = 80
CONTRACT_MAX_BYTES = 8 * 1024
SKILL_DIR = ".claude/skills/project-icecrown-development"
ROLES_FILE = f"{SKILL_DIR}/references/recipes.md"
ROLES_HEADING = "Roles"
SESSION_AGENT = "the session"
POINTER_MAX_LINES = 6
ROLES_MIN_CELLS = 4  # role, agent, model, effort
AGENT_KEYS = ("name", "description", "tools", "model", "effort")
EVALS_FILE = "evals/evals.json"
ASK_FIRST_PREFIX = "ask-first:"
EXTERNAL = re.compile(r"^[a-z][a-z0-9+.-]*:", re.IGNORECASE)
CODE = re.compile(r"`([^`]+)`")


def check(root: Path) -> list[Violation]:
    """Return every guidance-integrity violation under ``root``."""
    violations = check_links(root, guidance_files(root))
    violations += check_contract_budget(root)
    violations += check_routing_table(root)
    violations += check_pointer_files(root)
    violations += check_agents(root)
    violations += check_evals(root)
    return violations


def guidance_files(root: Path) -> list[Path]:
    """Return the Markdown files whose links and anchors are checked."""
    files = [root / name for name in TOP_LEVEL_GUIDANCE if (root / name).is_file()]
    claude = root / ".claude"
    if claude.is_dir():
        files += sorted(claude.rglob("*.md"))
    return files


def check_links(root: Path, files: Sequence[Path]) -> list[Violation]:
    """G1: relative links resolve to files, and anchors to headings."""
    found = []
    slug_cache: dict[Path, set[str]] = {}
    for path in files:
        rel = path.relative_to(root).as_posix()
        for line, target in iter_links(path.read_text(encoding="utf-8")):
            if EXTERNAL.match(target):
                continue
            file_part, _, anchor = target.partition("#")
            dest = (path.parent / file_part).resolve() if file_part else path.resolve()
            if not dest.is_relative_to(root.resolve()):
                found.append(Violation(rel, line, "G1", f"link leaves the repository: {target}"))
                continue
            if not dest.exists():
                found.append(Violation(rel, line, "G1", f"broken link: {target}"))
                continue
            if anchor and dest.suffix == ".md":
                if dest not in slug_cache:
                    slug_cache[dest] = heading_slugs(dest.read_text(encoding="utf-8"))
                if anchor not in slug_cache[dest]:
                    found.append(Violation(rel, line, "G1", f"missing anchor: {target}"))
    return found


def check_contract_budget(root: Path) -> list[Violation]:
    """G2: the operating contract stays within its line and byte budget."""
    path = root / CONTRACT
    if not path.is_file():
        return [Violation(CONTRACT, 1, "G2", "the operating contract is missing")]
    data = path.read_bytes()
    lines = len(data.decode("utf-8").splitlines())
    found = []
    if lines > CONTRACT_MAX_LINES:
        found.append(Violation(CONTRACT, 1, "G2", f"{lines} lines (at most {CONTRACT_MAX_LINES})"))
    if len(data) > CONTRACT_MAX_BYTES:
        found.append(Violation(CONTRACT, 1, "G2", f"{len(data)} bytes (at most 8 KiB)"))
    return found


def check_routing_table(root: Path) -> list[Violation]:
    """G3: the skill's routing table has exactly one row per reference file."""
    skill = root / SKILL_DIR / "SKILL.md"
    if not skill.is_file():
        return [Violation(f"{SKILL_DIR}/SKILL.md", 1, "G3", "the development skill is missing")]
    rel = skill.relative_to(root).as_posix()
    rows: dict[str, list[int]] = {}
    for line, cells in table_rows(skill.read_text(encoding="utf-8")):
        targets = {
            (skill.parent / target.partition("#")[0]).resolve()
            for _, target in iter_links(" | ".join(cells))
            if not EXTERNAL.match(target)
        }
        for target in targets:
            if target.is_relative_to(skill.parent.resolve()):
                name = target.relative_to(skill.parent.resolve()).as_posix()
                rows.setdefault(name, []).append(line)
    references = skill.parent / "references"
    expected = (
        {p.relative_to(skill.parent).as_posix() for p in references.rglob("*.md")}
        if references.is_dir()
        else set()
    )
    found = [
        Violation(rel, 1, "G3", f"no routing row for {name}")
        for name in sorted(expected - rows.keys())
    ]
    found += [
        Violation(rel, lines[1], "G3", f"{name} is routed by {len(lines)} rows")
        for name, lines in sorted(rows.items())
        if name in expected and len(lines) > 1
    ]
    return found


def check_pointer_files(root: Path) -> list[Violation]:
    """G4 and G5: rules and command skills are short and pointer-only."""
    found = []
    rules = root / ".claude" / "rules"
    for path in sorted(rules.glob("*.md")) if rules.is_dir() else []:
        meta, body = split_frontmatter(path.read_text(encoding="utf-8"))
        rel = path.relative_to(root).as_posix()
        paths = meta.get("paths")
        if not isinstance(paths, list) or not paths:
            found.append(Violation(rel, 1, "G4", "frontmatter needs a non-empty 'paths' list"))
        found += _pointer_body(rel, body, "G4")
    skills = root / ".claude" / "skills"
    for path in sorted(skills.glob("*/SKILL.md")) if skills.is_dir() else []:
        if path.parent == root / SKILL_DIR:
            continue
        meta, body = split_frontmatter(path.read_text(encoding="utf-8"))
        rel = path.relative_to(root).as_posix()
        found += [
            Violation(rel, 1, "G5", f"frontmatter needs '{key}'")
            for key in ("name", "description")
            if not meta.get(key)
        ]
        found += _pointer_body(rel, body, "G5")
    return found


def _pointer_body(rel: str, body: Sequence[tuple[int, str]], code: str) -> list[Violation]:
    lines = [(number, text) for number, text in body if text.strip()]
    found = []
    if len(lines) > POINTER_MAX_LINES:
        found.append(
            Violation(rel, lines[0][0], code, f"{len(lines)} body lines (at most 6, pointer-only)")
        )
    found += [
        Violation(rel, number, code, "body line holds no link (pointer-only)")
        for number, text in lines
        if not any(True for _ in iter_links(text))
    ]
    return found


def roles(root: Path) -> dict[str, tuple[int, str, str]]:
    """Return the roles table as ``{agent: (line, model, effort)}``."""
    path = root / ROLES_FILE
    if not path.is_file():
        return {}
    table: dict[str, tuple[int, str, str]] = {}
    for line, cells in table_rows(path.read_text(encoding="utf-8"), heading=ROLES_HEADING):
        if len(cells) < ROLES_MIN_CELLS:
            continue
        agent, model, effort = (_code_or_text(cell) for cell in cells[1:4])
        table[agent] = (line, model, effort)
    return table


def _code_or_text(cell: str) -> str:
    match = CODE.search(cell)
    return match.group(1) if match else cell.strip()


def check_agents(root: Path) -> list[Violation]:
    """G6: agents declare their keys and match the roles table, as does the session."""
    table = roles(root)
    found = []
    agents_dir = root / ".claude" / "agents"
    seen: set[str] = set()
    for path in sorted(agents_dir.glob("*.md")) if agents_dir.is_dir() else []:
        rel = path.relative_to(root).as_posix()
        meta, _ = split_frontmatter(path.read_text(encoding="utf-8"))
        found += [
            Violation(rel, 1, "G6", f"frontmatter needs '{key}'")
            for key in AGENT_KEYS
            if not meta.get(key)
        ]
        name = str(meta.get("name", path.stem))
        seen.add(name)
        found += _compare_role(rel, name, meta.get("model"), meta.get("effort"), table)
    found += [
        Violation(ROLES_FILE, line, "G6", f"roles table names {agent!r}, which has no agent file")
        for agent, (line, _, _) in sorted(table.items())
        if agent not in seen and agent != SESSION_AGENT
    ]
    settings = root / ".claude" / "settings.json"
    if settings.is_file() and SESSION_AGENT in table:
        try:
            data = json.loads(settings.read_text(encoding="utf-8"))
        except json.JSONDecodeError as err:
            return [*found, Violation(".claude/settings.json", err.lineno, "G6", "invalid JSON")]
        if not isinstance(data, dict):
            return [*found, Violation(".claude/settings.json", 1, "G6", "expected an object")]
        model, effort = data.get("model"), data.get("effortLevel")
        found += _compare_role(".claude/settings.json", SESSION_AGENT, model, effort, table)
    return found


def _compare_role(
    rel: str,
    name: str,
    model: object,
    effort: object,
    table: dict[str, tuple[int, str, str]],
) -> list[Violation]:
    if name not in table:
        return [Violation(rel, 1, "G6", f"{name!r} has no row in the roles table")]
    _, want_model, want_effort = table[name]
    found = []
    if model != want_model:
        found.append(
            Violation(rel, 1, "G6", f"model {model!r}; the roles table says {want_model!r}")
        )
    if effort != want_effort:
        message = f"effort {effort!r}; the roles table says {want_effort!r}"
        found.append(Violation(rel, 1, "G6", message))
    return found


def routed_references(root: Path) -> set[str]:
    """Return the reference files the routing table routes to, relative to the skill directory."""
    skill = root / SKILL_DIR / "SKILL.md"
    if not skill.is_file():
        return set()
    base = skill.parent.resolve()
    routed = set()
    for _, cells in table_rows(skill.read_text(encoding="utf-8")):
        for _, target in iter_links(" | ".join(cells)):
            dest = (skill.parent / target.partition("#")[0]).resolve()
            if not EXTERNAL.match(target) and dest.is_relative_to(base / "references"):
                routed.add(dest.relative_to(base).as_posix())
    return routed


def check_evals(root: Path) -> list[Violation]:
    """G7: the routing and ask-first evals parse and name a routed file or an ask-first item."""
    path = root / EVALS_FILE
    if not path.is_file():
        return [Violation(EVALS_FILE, 1, "G7", "the evals file is missing")]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as err:
        return [Violation(EVALS_FILE, err.lineno, "G7", f"invalid JSON: {err.msg}")]
    evals = data.get("evals") if isinstance(data, dict) else None
    if not isinstance(evals, list) or not evals:
        return [Violation(EVALS_FILE, 1, "G7", "expected a non-empty 'evals' list")]
    routed = routed_references(root)
    found = []
    ids: set[str] = set()
    for index, item in enumerate(evals):
        if not isinstance(item, dict) or not all(
            isinstance(item.get(key), str) and item[key] for key in ("id", "prompt", "expect")
        ):
            found.append(
                Violation(EVALS_FILE, 1, "G7", f"eval #{index} needs string id, prompt, expect")
            )
            continue
        if item["id"] in ids:
            found.append(Violation(EVALS_FILE, 1, "G7", f"duplicate eval id {item['id']!r}"))
        ids.add(item["id"])
        expect = item["expect"]
        if expect.startswith(ASK_FIRST_PREFIX):
            if not expect.removeprefix(ASK_FIRST_PREFIX).strip():
                found.append(
                    Violation(EVALS_FILE, 1, "G7", f"{item['id']}: name the ask-first item")
                )
        elif expect not in routed:
            found.append(Violation(EVALS_FILE, 1, "G7", f"{item['id']}: unknown route {expect!r}"))
    return found


def main(argv: Sequence[str] | None = None) -> int:
    """Run the guidance-integrity checks and return the exit code."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=repo_root(), help="repository root")
    args = parser.parse_args(argv)
    return report(check(args.root), "check_guidance_integrity")


if __name__ == "__main__":
    sys.exit(main())
