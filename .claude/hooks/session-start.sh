#!/usr/bin/env bash
# SessionStart hook: prepare the development environment in Claude Code cloud sessions.
# Local sessions are left alone; set ICECROWN_SKIP_DEV_SETUP=1 to skip it in the cloud too.
set -euo pipefail

if [[ "${CLAUDE_CODE_REMOTE:-}" != "true" || "${ICECROWN_SKIP_DEV_SETUP:-}" == "1" ]]; then
  exit 0
fi

cd "${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel)}"

if ! command -v uv >/dev/null 2>&1; then
  echo "session-start: uv is not installed; skipping the development setup." >&2
  exit 0
fi

uv sync --frozen --quiet
uv run --frozen pre-commit install --hook-type pre-commit --hook-type commit-msg >/dev/null
echo "Development environment ready: dependencies synced from uv.lock, git hooks installed."
