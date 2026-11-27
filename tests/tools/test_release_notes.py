"""The release-notes tool: tag check and changelog sections."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

import release_notes as rn

if TYPE_CHECKING:
    from pathlib import Path

CHANGELOG = """# Changelog

## [Unreleased]

### Added

- Something new.

## [0.1.0] - 2026-12-01

### Added

- The first release.

[Unreleased]: https://example.com/compare/v0.1.0...HEAD
[0.1.0]: https://example.com/releases/v0.1.0
"""


def make_root(tmp_path: Path, version: str, changelog: str = CHANGELOG) -> Path:
    (tmp_path / "pyproject.toml").write_text(
        f'[project]\nversion = "{version}"\n', encoding="utf-8"
    )
    (tmp_path / "CHANGELOG.md").write_text(changelog, encoding="utf-8")
    return tmp_path


@pytest.mark.parametrize(
    ("version", "expected"),
    [("0.1.0", False), ("0.1.0.dev0", True), ("1.0.0rc1", True), ("2.0a3", True), ("1.2", False)],
)
def test_prerelease_detection(version: str, expected: bool) -> None:
    assert rn.is_prerelease(version) is expected


def test_a_release_gets_its_own_section(tmp_path: Path) -> None:
    body, error = rn.notes(make_root(tmp_path, "0.1.0"), "v0.1.0")
    assert error == ""
    assert body == "### Added\n\n- The first release."


def test_a_rehearsal_without_an_entry_gets_unreleased(tmp_path: Path) -> None:
    body, _ = rn.notes(make_root(tmp_path, "0.2.0.dev0"), "v0.2.0.dev0")
    assert body == "### Added\n\n- Something new."


def test_a_release_without_an_entry_fails(tmp_path: Path) -> None:
    body, error = rn.notes(make_root(tmp_path, "0.2.0"), "v0.2.0")
    assert body is None
    assert "no entry for 0.2.0" in error


def test_a_mismatched_tag_fails(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    root = make_root(tmp_path, "0.1.0")
    assert rn.main(["v0.1.1", "--root", str(root)]) == 1
    assert "does not match" in capsys.readouterr().err


def test_is_prerelease_flag(tmp_path: Path) -> None:
    root = str(make_root(tmp_path, "0.1.0"))
    assert rn.main(["v0.1.0.dev0", "--root", root, "--is-prerelease"]) == 0
    assert rn.main(["v0.1.0", "--root", root, "--is-prerelease"]) == 1


def test_without_a_tag_the_current_version_is_checked(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert rn.main(["--root", str(make_root(tmp_path, "0.1.0"))]) == 0
    assert capsys.readouterr().out == "### Added\n\n- The first release.\n"
    assert rn.main(["--root", str(make_root(tmp_path, "0.3.0"))]) == 1


def test_main_prints_the_notes(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert rn.main(["v0.1.0", "--root", str(make_root(tmp_path, "0.1.0"))]) == 0
    assert capsys.readouterr().out == "### Added\n\n- The first release.\n"
