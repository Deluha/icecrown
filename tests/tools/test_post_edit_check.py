"""The post-edit Claude Code hook: which edited files it lints."""

from __future__ import annotations

import importlib.util
import json
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
