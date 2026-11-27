"""The verify command: step selection, running and rendering."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

import verify

if TYPE_CHECKING:
    from collections.abc import Sequence


def test_steps_run_in_the_documented_order() -> None:
    names = [step.name for step in verify.steps("main")]
    assert names == [
        "conventions",
        "guidance",
        "docs-sync",
        "ruff-check",
        "ruff-format",
        "mypy",
        "tests",
    ]


def test_docs_sync_is_skipped_without_a_base_ref() -> None:
    step = next(s for s in verify.steps(None) if s.name == "docs-sync")
    assert verify.run_step(step, Path()).status == "skip"


def test_no_base_ref_outside_a_checkout(tmp_path: Path) -> None:
    assert verify.base_ref(tmp_path) is None


def test_no_base_ref_without_a_main_branch(tmp_path: Path) -> None:
    def git(*args: str) -> None:
        subprocess.run(
            ["git", "-c", "user.name=t", "-c", "user.email=t@example.invalid", *args],
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )

    git("init", "-q", "-b", "other")
    git("commit", "-q", "--allow-empty", "-m", "start")
    assert verify.base_ref(tmp_path) is None


def test_a_step_stops_at_its_first_failing_command() -> None:
    calls: list[str] = []

    def runner(command: Sequence[str], cwd: Path) -> tuple[int, str]:
        del cwd
        calls.append(command[0])
        return (1 if command[0] == "b" else 0), f"{command[0]} ran\n"

    step = verify.Step("x", (("a",), ("b",), ("c",)))
    outcome = verify.run_step(step, Path(), runner)
    assert outcome.status == "FAIL"
    assert calls == ["a", "b"]
    assert outcome.output == "a ran\nb ran\n"


def test_render_shows_the_table_and_failure_output() -> None:
    table = verify.render(
        [
            verify.Outcome("lint", "pass", 0.25, "quiet"),
            verify.Outcome("tests", "FAIL", 1.0, "boom\n"),
        ]
    )
    assert table.splitlines()[:4] == [
        "| Check | Result | Seconds |",
        "|-------|--------|---------|",
        "| lint  | pass   |     0.2 |",
        "| tests | FAIL   |     1.0 |",
    ]
    assert table.endswith("--- tests ---\nboom")
    assert "quiet" not in table


def test_list_and_unknown_steps(capsys: pytest.CaptureFixture[str]) -> None:
    assert verify.main(["--list"]) == 0
    assert "tests" in capsys.readouterr().out.split()
    with pytest.raises(SystemExit):
        verify.main(["--only", "nope"])
