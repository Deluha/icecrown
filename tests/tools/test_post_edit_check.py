"""The post-edit Claude Code hook: which edited files it lints."""

from __future__ import annotations

import importlib.util
import io
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from types import ModuleType

HOOK = Path(__file__).resolve().parents[2] / ".claude" / "hooks" / "post_edit_check.py"


@pytest.fixture(scope="module")
def hook() -> ModuleType:
    spec = importlib.util.spec_from_file_location("post_edit_check", HOOK)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def payload(path: object) -> str:
    return json.dumps({"tool_name": "Edit", "tool_input": {"file_path": path}})


def test_a_python_file_in_the_project_is_checked(hook: ModuleType, tmp_path: Path) -> None:
    target = tmp_path / "x.py"
    target.write_text("", encoding="utf-8")
    assert hook.file_to_check(payload(str(target)), tmp_path) == target.resolve()


@pytest.mark.parametrize("raw", ["not json", json.dumps([1]), json.dumps({"tool_input": 3})])
def test_unreadable_payloads_are_ignored(hook: ModuleType, tmp_path: Path, raw: str) -> None:
    assert hook.file_to_check(raw, tmp_path) is None


def test_other_files_are_ignored(hook: ModuleType, tmp_path: Path) -> None:
    (tmp_path / "x.md").write_text("", encoding="utf-8")
    outside = tmp_path.parent / "outside.py"
    assert hook.file_to_check(payload(str(tmp_path / "x.md")), tmp_path) is None
    assert hook.file_to_check(payload(str(tmp_path / "missing.py")), tmp_path) is None
    assert hook.file_to_check(payload(str(outside)), tmp_path) is None
    assert hook.file_to_check(payload(None), tmp_path) is None


class FakeResult:
    def __init__(self, returncode: int) -> None:
        self.returncode = returncode
        self.stdout = "F401 unused import\n"
        self.stderr = ""


def fake_ruff(project: Path) -> Path:
    ruff = project / ".venv" / "bin" / "ruff"
    ruff.parent.mkdir(parents=True)
    ruff.write_text("", encoding="utf-8")
    return ruff


@pytest.mark.parametrize(("ruff_exit", "hook_exit"), [(0, 0), (1, 2), (2, 0)])
def test_main_blocks_only_on_ruff_findings(
    hook: ModuleType,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    ruff_exit: int,
    hook_exit: int,
) -> None:
    target = tmp_path / "x.py"
    target.write_text("import os\n", encoding="utf-8")
    ruff = fake_ruff(tmp_path)
    calls: list[list[str]] = []

    def run(command: list[str], **_: object) -> FakeResult:
        calls.append(command)
        return FakeResult(ruff_exit)

    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
    monkeypatch.setattr("sys.stdin", io.StringIO(payload(str(target))))
    monkeypatch.setattr(hook.subprocess, "run", run)
    assert hook.main() == hook_exit
    assert calls[0][0] == str(ruff)
    err = capsys.readouterr().err
    assert ("F401" in err) is (hook_exit == hook.BLOCKING_EXIT)


def test_main_without_a_synced_environment_does_nothing(
    hook: ModuleType, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = tmp_path / "x.py"
    target.write_text("", encoding="utf-8")
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
    monkeypatch.setattr("sys.stdin", io.StringIO(payload(str(target))))
    assert hook.main() == 0


def test_the_windows_layout_is_found(hook: ModuleType, tmp_path: Path) -> None:
    ruff = tmp_path / ".venv" / "Scripts" / "ruff.exe"
    ruff.parent.mkdir(parents=True)
    ruff.write_text("", encoding="utf-8")
    assert hook.locked_ruff(tmp_path) == ruff


@pytest.mark.skipif(sys.platform == "win32", reason="the hook is a bash script")
def test_session_start_survives_a_refused_hook_install(tmp_path: Path) -> None:
    script = HOOK.parent / "session-start.sh"
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    fake_uv = bin_dir / "uv"
    fake_uv.write_text('#!/bin/sh\ncase "$*" in *"pre-commit install"*) exit 1;; esac\nexit 0\n')
    fake_uv.chmod(0o755)
    env = {
        "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}",
        "CLAUDE_CODE_REMOTE": "true",
        "CLAUDE_PROJECT_DIR": str(tmp_path),
    }
    result = subprocess.run(
        ["bash", str(script)], env=env, capture_output=True, text=True, check=False
    )
    assert result.returncode == 0
    assert "git hooks were not installed" in result.stderr


@pytest.mark.skipif(sys.platform == "win32", reason="the hook is a bash script")
def test_session_start_does_nothing_locally(tmp_path: Path) -> None:
    script = HOOK.parent / "session-start.sh"
    env = {"PATH": os.environ["PATH"], "CLAUDE_PROJECT_DIR": str(tmp_path)}
    result = subprocess.run(
        ["bash", str(script)], env=env, capture_output=True, text=True, check=False
    )
    assert (result.returncode, result.stdout, result.stderr) == (0, "", "")
