"""Helpers shared by the checkers: violations, file listing, Markdown and frontmatter parsing."""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator

Frontmatter = dict[str, str | list[str]]

_LINK = re.compile(r"(?<!!)\[(?:[^\]\\]|\\.)*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
_INLINE_CODE = re.compile(r"`[^`]*`")
_HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
_FENCE = re.compile(r"^\s{0,3}(`{3,}|~{3,})")
_LINK_TEXT = re.compile(r"!?\[((?:[^\]\\]|\\.)*)\]\([^)]*\)")
_SKIPPED_DIRS = frozenset({".git", ".venv", "build", "dist", "node_modules", "__pycache__"})
_SLUG_DROP = re.compile(r"[^\w\- ]", re.UNICODE)
_TABLE_HEADER_LINES = 2  # the header row and the separator row


@dataclass(frozen=True, order=True)
class Violation:
    """One broken rule at one place in the repository."""

    path: str
    line: int
    code: str
    message: str

    def __str__(self) -> str:
        """Render as ``path:line: CODE message``."""
        return f"{self.path}:{self.line}: {self.code} {self.message}"


def repo_root() -> Path:
    """Return the repository root: the parent of the ``tools/`` directory."""
    return Path(__file__).resolve().parent.parent


def list_files(root: Path) -> list[str]:
    """Return the repository's files as POSIX paths relative to ``root``.

    In a git checkout these are the tracked and the untracked, not-ignored files; elsewhere (for
    example a test's temporary directory) every file under ``root``.
    """
    if (root / ".git").exists():
        out = subprocess.run(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
            cwd=root,
            capture_output=True,
            check=True,
        ).stdout.decode()
        return sorted({p for p in out.split("\0") if p and (root / p).is_file()})
    return sorted(
        p.relative_to(root).as_posix()
        for p in root.rglob("*")
        if p.is_file() and not _SKIPPED_DIRS.intersection(p.relative_to(root).parts[:-1])
    )


def report(violations: Iterable[Violation], name: str) -> int:
    """Print the violations, or a one-line success message, and return the exit code."""
    found = sorted(violations)
    for violation in found:
        print(violation)
    if found:
        print(f"{name}: {len(found)} violation(s)")
        return 1
    print(f"{name}: ok")
    return 0


def markdown_lines(text: str, *, keep_inline_code: bool = False) -> Iterator[tuple[int, str]]:
    """Yield ``(line_number, line)`` for lines outside fenced code blocks.

    Inline code spans are removed unless ``keep_inline_code`` is set.
    """
    fence: str | None = None  # the opening fence, while inside a fenced block
    for number, line in enumerate(text.splitlines(), start=1):
        match = _FENCE.match(line)
        if fence is None and match:
            fence = match.group(1)
            continue
        if fence is not None:
            closing = line.strip()
            if closing and set(closing) == {fence[0]} and len(closing) >= len(fence):
                fence = None
            continue
        yield number, line if keep_inline_code else _INLINE_CODE.sub("", line)


def iter_links(text: str) -> Iterator[tuple[int, str]]:
    """Yield ``(line_number, target)`` for every Markdown link outside code."""
    for number, line in markdown_lines(text):
        for match in _LINK.finditer(line):
            yield number, match.group(1)


def heading_slugs(text: str) -> set[str]:
    """Return the GitHub-style anchor of every heading, with ``-1``, ``-2`` for repeats."""
    slugs: set[str] = set()
    counts: dict[str, int] = {}
    for _, line in markdown_lines(text, keep_inline_code=True):
        match = _HEADING.match(line)
        if not match:
            continue
        title = _LINK_TEXT.sub(r"\1", match.group(2)).replace("`", "")
        base = _SLUG_DROP.sub("", title.strip().lower()).replace(" ", "-")
        seen = counts.get(base, 0)
        counts[base] = seen + 1
        slugs.add(base if seen == 0 else f"{base}-{seen}")
    return slugs


def split_frontmatter(text: str) -> tuple[Frontmatter, list[tuple[int, str]]]:
    """Split a Markdown file into its YAML frontmatter and its numbered body lines.

    Only the subset the guidance uses is understood: ``key: value``, ``key: [a, b]`` and a key
    followed by ``- item`` lines. A file without frontmatter returns an empty mapping.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, list(enumerate(lines, start=1))
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration:
        return {}, list(enumerate(lines, start=1))
    data: Frontmatter = {}
    key: str | None = None
    for raw in lines[1:end]:
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("- ") and key is not None:
            current = data.get(key)
            items = current if isinstance(current, list) else []
            items.append(_unquote(stripped[2:]))
            data[key] = items
            continue
        name, _, value = stripped.partition(":")
        key = name.strip()
        value = value.strip()
        if value.startswith("[") and value.endswith("]"):
            data[key] = [_unquote(v) for v in value[1:-1].split(",") if v.strip()]
        else:
            data[key] = _unquote(value)
    body = [(i + 1, lines[i]) for i in range(end + 1, len(lines))]
    return data, body


def _unquote(value: str) -> str:
    value = value.strip()
    if len(value) > 1 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def table_rows(text: str, heading: str | None = None) -> list[tuple[int, list[str]]]:
    """Return the body rows of the Markdown tables in ``text`` as ``(line, cells)``.

    A table is a run of lines starting with ``|``; its first line is the header and its second the
    separator, and both are skipped. With ``heading``, only tables under that heading (until the
    next heading of any level) count.
    """
    rows: list[tuple[int, list[str]]] = []
    in_section = heading is None
    position_in_table = 0
    for number, line in markdown_lines(text, keep_inline_code=True):
        match = _HEADING.match(line)
        if match:
            in_section = heading is None or match.group(2).strip() == heading
        stripped = line.strip()
        if not stripped.startswith("|"):
            position_in_table = 0
            continue
        position_in_table += 1
        if in_section and position_in_table > _TABLE_HEADER_LINES:
            rows.append((number, [cell.strip() for cell in stripped.strip("|").split("|")]))
    return rows
