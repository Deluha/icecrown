"""The docs-sync checker: areas, the skip marker, and the git-backed modes."""

from __future__ import annotations

import os
import subprocess
from typing import TYPE_CHECKING

import pytest

import check_docs_sync as ds

if TYPE_CHECKING:
    from pathlib import Path

CHECKERS_DOC = f"{ds.REFERENCES}/checkers.md"
QA_DOC = f"{ds.REFERENCES}/qa-and-ci.md"


@pytest.mark.parametrize(
    ("files", "missing"),
    [
        (["src/icecrown/_x.py"], ["package code"]),
        (["src/icecrown/_x.py", "docs/index.md"], []),
        (["tools/verify.py"], ["checkers"]),
        (["tools/verify.py", CHECKERS_DOC], []),
        ([".github/workflows/ci.yml", ".claude/hooks/x.py"], ["CI and hooks"]),
        ([".pre-commit-config.yaml", QA_DOC], []),
        (["README.md", "tests/test_x.py"], []),
    ],
)
def test_missing_docs(files: list[str], missing: list[str]) -> None:
    assert [area.name for area in ds.missing_docs(files)] == missing


def test_skip_marker_must_be_its_own_body_line() -> None:
    assert ds.has_skip_marker("Subject\n\nBody\n[skip-docs]\n")
    assert ds.has_skip_marker("Subject\n\n  [skip-docs]  \n")
    assert not ds.has_skip_marker("[skip-docs]\n\nBody\n")
    assert not ds.has_skip_marker("Subject\n\nsee [skip-docs] here\n")
    assert not ds.has_skip_marker("Subject\n\n# [skip-docs]\n")


def test_a_doc_anywhere_in_the_set_counts(capsys: pytest.CaptureFixture[str]) -> None:
    changes: list[tuple[str | None, list[str]]] = [
        ("Code\n", ["src/icecrown/_x.py"]),
        ("Docs\n", ["docs/x.md"]),
    ]
    assert ds.evaluate(changes) == 0
    assert "ok" in capsys.readouterr().out


def test_the_marker_waives_only_its_own_commit(capsys: pytest.CaptureFixture[str]) -> None:
    changes: list[tuple[str | None, list[str]]] = [
        ("Skeleton\n\n[skip-docs]\n", ["src/icecrown/_x.py"]),
        ("Tool\n", ["tools/x.py"]),
        (None, []),
    ]
    assert ds.evaluate(changes) == 1
    out = capsys.readouterr().out
    assert "checkers changed" in out
    assert "package code" not in out


def git(root: Path, *args: str) -> str:
    env = {
        **os.environ,
        "GIT_AUTHOR_NAME": "t",
        "GIT_AUTHOR_EMAIL": "t@example.invalid",
        "GIT_COMMITTER_NAME": "t",
        "GIT_COMMITTER_EMAIL": "t@example.invalid",
    }
    return subprocess.run(
        ["git", "-c", "core.hooksPath=/dev/null", "-c", "commit.gpgsign=false", *args],
        cwd=root,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    ).stdout


def commit(root: Path, rel: str, message: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(message, encoding="utf-8")
    git(root, "add", rel)
    git(root, "commit", "-q", "-m", message)


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    git(tmp_path, "init", "-q", "-b", "main")
    commit(tmp_path, "README.md", "Start")
    git(tmp_path, "checkout", "-q", "-b", "work")
    return tmp_path


def test_range_mode(repo: Path) -> None:
    commit(repo, "src/icecrown/_x.py", "Add code")
    assert ds.main(["--root", str(repo), "--range", "main..work"]) == 1
    commit(repo, "docs/x.md", "Document it")
    assert ds.main(["--root", str(repo), "--range", "main...work"]) == 0


def test_base_mode_includes_uncommitted_work(repo: Path) -> None:
    assert ds.main(["--root", str(repo), "--base", "main"]) == 0
    (repo / "tools").mkdir()
    (repo / "tools" / "x.py").write_text("", encoding="utf-8")
    assert ds.main(["--root", str(repo), "--base", "main"]) == 1


def test_commit_msg_mode(repo: Path, tmp_path_factory: pytest.TempPathFactory) -> None:
    (repo / "tools").mkdir()
    (repo / "tools" / "x.py").write_text("", encoding="utf-8")
    git(repo, "add", "tools/x.py")
    message = tmp_path_factory.mktemp("msg") / "COMMIT_EDITMSG"
    message.write_text("Add a tool\n", encoding="utf-8")
    assert ds.main(["--root", str(repo), "--commit-msg", str(message)]) == 1
    message.write_text("Add a tool\n\n[skip-docs]\n", encoding="utf-8")
    assert ds.main(["--root", str(repo), "--commit-msg", str(message)]) == 0


def test_non_ascii_paths_are_matched(repo: Path) -> None:
    commit(repo, "src/icecrown/_données.py", "Add code")
    assert ds.main(["--root", str(repo), "--range", "main..work"]) == 1


def test_an_unknown_ref_is_reported_not_raised(
    repo: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert ds.main(["--root", str(repo), "--base", "no-such-ref"]) == 2
    assert "git failed" in capsys.readouterr().out


def test_malformed_range_is_a_usage_error(repo: Path) -> None:
    with pytest.raises(SystemExit) as exc:
        ds.main(["--root", str(repo), "--range", "main"])
    assert exc.value.code == 2
