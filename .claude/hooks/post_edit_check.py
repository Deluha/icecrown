"""PostToolUse hook: lint a Python file right after Claude Code edits it.

Reads the hook payload from stdin. For an edited ``.py`` file inside the project, it runs the
ruff installed from ``uv.lock`` in the project's ``.venv`` on that file; on a finding it prints the
report to stderr and exits 2, which Claude Code feeds back to the session. Any other file, an
environment that is not synced yet, or a ruff that cannot run does not block.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

BLOCKING_EXIT = 2
RUFF_FOUND_PROBLEMS = 1  # ruff's exit code for findings; other codes mean it could not run


def file_to_check(payload: str, project_dir: Path) -> Path | None:
    """Return the edited Python file inside ``project_dir``, or None if there is nothing to lint."""
    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        return None
    tool_input = data.get("tool_input") if isinstance(data, dict) else None
    raw = tool_input.get("file_path") if isinstance(tool_input, dict) else None
    if not isinstance(raw, str) or not raw.endswith(".py"):
        return None
    path = Path(raw).resolve()
    if not path.is_file() or not path.is_relative_to(project_dir.resolve()):
        return None
    return path


def locked_ruff(project_dir: Path) -> Path | None:
    """Return the ruff installed from ``uv.lock`` in the project's ``.venv``, if there is one."""
    for relative in (".venv/bin/ruff", ".venv/Scripts/ruff.exe"):
        candidate = project_dir / relative
        if candidate.is_file():
            return candidate
    return None


def main() -> int:
    """Run the hook and return its exit code."""
    project_dir = Path(os.environ.get("CLAUDE_PROJECT_DIR") or Path.cwd())
    path = file_to_check(sys.stdin.read(), project_dir)
    ruff = locked_ruff(project_dir)
    if path is None or ruff is None:
        return 0
    result = subprocess.run(
        [str(ruff), "check", "--quiet", "--force-exclude", str(path)],
        capture_output=True,
        text=True,
        check=False,
        cwd=project_dir,
    )
    if result.returncode == 0:
        return 0
    if result.returncode != RUFF_FOUND_PROBLEMS:
        sys.stderr.write(
            f"post_edit_check: could not run ruff ({result.stderr.strip()}); skipped\n"
        )
        return 0
    sys.stderr.write(f"ruff check found problems in {path.name}:\n{result.stdout}{result.stderr}")
    return BLOCKING_EXIT


if __name__ == "__main__":
    sys.exit(main())
