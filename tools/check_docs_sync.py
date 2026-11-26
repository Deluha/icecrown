"""Check that a change in a documented area also changes its doc (hard rule R7).

The areas and their docs are listed in
``.claude/skills/project-icecrown-development/references/checkers.md``. A line that is exactly
``[skip-docs]`` in a commit body waives the check for that commit.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from _toolkit import repo_root

if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence

SKIP_MARKER = "[skip-docs]"
REFERENCES = ".claude/skills/project-icecrown-development/references"


@dataclass(frozen=True)
class Area:
    """A documented code area and its doc: a file, or a directory ending in ``/``."""

    name: str
    prefixes: tuple[str, ...]
    doc: str

    def is_doc(self, path: str) -> bool:
        """Return whether ``path`` is this area's doc."""
        return path.startswith(self.doc) if self.doc.endswith("/") else path == self.doc


AREAS = (
    Area("package code", ("src/icecrown/",), "docs/"),
    Area("checkers", ("tools/",), f"{REFERENCES}/checkers.md"),
    Area(
        "CI and hooks",
        (".github/workflows/", ".pre-commit-config.yaml", ".claude/hooks/"),
        f"{REFERENCES}/qa-and-ci.md",
    ),
)


def missing_docs(files: Iterable[str]) -> list[Area]:
    """Return the areas touched by ``files`` whose doc is not among them."""
    changed = set(files)
    return [
        area
        for area in AREAS
        if any(f.startswith(area.prefixes) for f in changed)
        and not any(area.is_doc(f) for f in changed)
    ]


def has_skip_marker(message: str) -> bool:
    """Return whether a commit message's body holds the ``[skip-docs]`` line."""
    body = [line.strip() for line in message.splitlines()[1:] if not line.startswith("#")]
    return SKIP_MARKER in body


def _git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-c", "core.quotePath=false", *args],
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
    ).stdout


def _lines(text: str) -> list[str]:
    return [line for line in text.splitlines() if line]


def staged_files(root: Path) -> list[str]:
    """Return the files staged for the commit being made."""
    return _lines(_git(root, "diff", "--cached", "--name-only"))


def range_commits(root: Path, base: str, head: str) -> list[tuple[str, list[str]]]:
    """Return ``(message, files)`` for each commit in ``base..head``."""
    commits = []
    for sha in _lines(_git(root, "rev-list", "--no-merges", f"{base}..{head}")):
        message = _git(root, "log", "-1", "--format=%B", sha)
        files = _lines(_git(root, "show", "--name-only", "--format=", sha))
        commits.append((message, files))
    return commits


def uncommitted_files(root: Path) -> list[str]:
    """Return the files changed in the working tree or index, and the untracked ones."""
    changed = _lines(_git(root, "diff", "--name-only", "HEAD"))
    return changed + _lines(_git(root, "ls-files", "--others", "--exclude-standard"))


def evaluate(changes: Sequence[tuple[str | None, Sequence[str]]]) -> int:
    """Print the outcome for a set of changes and return the exit code.

    Each change is a commit message (None for uncommitted work) and its files. A doc changed
    anywhere in the set counts for the whole set; a change whose message holds the skip marker
    needs no doc.
    """
    every_file = [f for _, files in changes for f in files]
    needing = [f for message, files in changes if not _waived(message) for f in files]
    missing = [area for area in missing_docs(needing) if area in missing_docs(every_file)]
    for area in missing:
        print(
            f"check_docs_sync: {area.name} changed ({', '.join(area.prefixes)}) "
            f"but {area.doc} did not; update it, or add {SKIP_MARKER} on its own line "
            "in the commit body if there is nothing to document"
        )
    if not missing:
        print("check_docs_sync: ok")
    return 1 if missing else 0


def _waived(message: str | None) -> bool:
    return message is not None and has_skip_marker(message)


def main(argv: Sequence[str] | None = None) -> int:
    """Run the docs-sync check in one of its three modes and return the exit code."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=repo_root(), help="repository root")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--commit-msg", type=Path, metavar="FILE", help="commit-msg hook mode")
    mode.add_argument("--range", metavar="BASE..HEAD", help="check a commit range (CI)")
    mode.add_argument("--base", metavar="REF", help="check the work since the merge base with REF")
    args = parser.parse_args(argv)
    root: Path = args.root
    try:
        return _run(args, root, parser)
    except subprocess.CalledProcessError as err:
        print(
            f"check_docs_sync: git failed ({' '.join(err.cmd[3:])}): "
            f"{err.stderr.strip() or f'exit {err.returncode}'}; "
            "in a shallow clone, fetch more history (git fetch --unshallow)"
        )
        return 2


def _run(args: argparse.Namespace, root: Path, parser: argparse.ArgumentParser) -> int:
    if args.commit_msg is not None:
        message = args.commit_msg.read_text(encoding="utf-8")
        return evaluate([(message, staged_files(root))])
    if args.range is not None:
        base, sep, head = str(args.range).partition("..")
        if not sep or not base or not head:
            parser.error("--range takes BASE..HEAD")
        return evaluate(range_commits(root, base, head.lstrip(".")))
    merge_base = _git(root, "merge-base", args.base, "HEAD").strip()
    return evaluate([*range_commits(root, merge_base, "HEAD"), (None, uncommitted_files(root))])


if __name__ == "__main__":
    sys.exit(main())
