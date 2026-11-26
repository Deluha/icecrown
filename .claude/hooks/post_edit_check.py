"""PostToolUse hook: lint a Python file right after Claude Code edits it.

Reads the hook payload from stdin. For an edited ``.py`` file inside the project, it runs the
locked ``ruff check`` on that file; on a finding it prints the report to stderr and exits 2, which
Claude Code feeds back to the session. Anything else, or a missing ``uv``, exits 0 silently.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

BLOCKING_EXIT = 2


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


def main() -> int:
    """Run the hook and return its exit code."""
    project_dir = Path(os.environ.get("CLAUDE_PROJECT_DIR") or Path.cwd())
    path = file_to_check(sys.stdin.read(), project_dir)
    uv = shutil.which("uv")
    if path is None or uv is None:
        return 0
    result = subprocess.run(
        [uv, "run", "--frozen", "ruff", "check", "--quiet", "--force-exclude", str(path)],
        capture_output=True,
        text=True,
        check=False,
        cwd=project_dir,
    )
    if result.returncode == 0:
        return 0
    sys.stderr.write(f"ruff check found problems in {path.name}:\n{result.stdout}{result.stderr}")
    return BLOCKING_EXIT


if __name__ == "__main__":
    sys.exit(main())
