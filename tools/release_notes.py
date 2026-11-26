"""Check a release tag against the package version and print its changelog entry.

Usage: ``python tools/release_notes.py v0.1.0 [--is-prerelease]``. The release workflow runs it
before building, and again to create the GitHub Release. A pre-release without its own entry (a
``.devN`` rehearsal) gets the "Unreleased" section.
"""

from __future__ import annotations

import argparse
import re
import sys
import tomllib
from pathlib import Path
from typing import TYPE_CHECKING

from _toolkit import repo_root

if TYPE_CHECKING:
    from collections.abc import Sequence

PRERELEASE = re.compile(r"(a|b|rc|\.dev)\d+$")
UNRELEASED = "Unreleased"


def package_version(root: Path) -> str:
    """Return the version declared in ``pyproject.toml``."""
    data = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    return str(data["project"]["version"])


def is_prerelease(version: str) -> bool:
    """Return whether ``version`` is a pre-release or development release."""
    return PRERELEASE.search(version) is not None


def section(changelog: str, title: str) -> str | None:
    """Return the body of the ``## [title]`` section of a Keep a Changelog file, or None."""
    heading = re.compile(rf"^## \[{re.escape(title)}\](?:\s.*)?$", re.MULTILINE)
    match = heading.search(changelog)
    if match is None:
        return None
    following = re.compile(r"^## \[", re.MULTILINE).search(changelog, match.end())
    end = following.start() if following else len(changelog)
    body = re.sub(r"^\[[^\]]+\]: \S+\s*$", "", changelog[match.end() : end], flags=re.MULTILINE)
    return body.strip() or None


def notes(root: Path, tag: str) -> tuple[str | None, str]:
    """Return the release notes for ``tag`` and an error message (empty when there is none)."""
    version = package_version(root)
    if tag != f"v{version}":
        return None, f"tag {tag!r} does not match the package version {version!r} (want v{version})"
    changelog = (root / "CHANGELOG.md").read_text(encoding="utf-8")
    body = section(changelog, version)
    if body is None and is_prerelease(version):
        body = section(changelog, UNRELEASED)
    if body is None:
        return None, f"CHANGELOG.md has no entry for {version}"
    return body, ""


def main(argv: Sequence[str] | None = None) -> int:
    """Print the release notes for a tag, or an error, and return the exit code."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("tag", help="the release tag, for example v0.1.0")
    parser.add_argument("--root", type=Path, default=repo_root(), help="repository root")
    parser.add_argument(
        "--is-prerelease",
        action="store_true",
        help="print nothing; exit 0 if the tag is a pre-release, 1 if not",
    )
    args = parser.parse_args(argv)
    if args.is_prerelease:
        return 0 if is_prerelease(args.tag.removeprefix("v")) else 1
    body, error = notes(args.root, args.tag)
    if body is None:
        print(f"release_notes: {error}", file=sys.stderr)
        return 1
    print(body)
    return 0


if __name__ == "__main__":
    sys.exit(main())
