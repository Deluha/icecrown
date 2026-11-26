"""Run every gate a pull request needs and print one pass/fail table.

Usage: ``uv run python tools/verify.py [--only NAME ...] [--list]``. The gates are described in
``.claude/skills/project-icecrown-development/references/qa-and-ci.md``.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path

from _toolkit import repo_root

TOOLS = Path(__file__).resolve().parent
PYTHON = sys.executable
BASE_REFS = ("origin/main", "main")


@dataclass(frozen=True)
class Step:
    """One row of the table: a name and the commands it runs, in order."""

    name: str
    commands: tuple[tuple[str, ...], ...]


@dataclass(frozen=True)
class Outcome:
    """The result of one step."""

    name: str
    status: str  # "pass", "FAIL" or "skip"
    seconds: float
    output: str


Runner = Callable[[Sequence[str], Path], tuple[int, str]]


def _tool(script: str, *args: str) -> tuple[str, ...]:
    return (PYTHON, str(TOOLS / script), *args)


def _module(*args: str) -> tuple[str, ...]:
    return (PYTHON, "-m", *args)


def steps(base_ref: str | None) -> list[Step]:
    """Return the gates in the order they run."""
    docs_sync: tuple[tuple[str, ...], ...] = (
        (_tool("check_docs_sync.py", "--base", base_ref),) if base_ref else ()
    )
    return [
        Step("conventions", (_tool("check_conventions.py"),)),
        Step("guidance", (_tool("check_guidance_integrity.py"),)),
        Step("docs-sync", docs_sync),
        Step("ruff-check", (_module("ruff", "check"),)),
        Step("ruff-format", (_module("ruff", "format", "--check"),)),
        Step("mypy", (_module("mypy"),)),
        Step(
            "tests",
            (
                _module("coverage", "erase"),
                _module("coverage", "run", "-m", "pytest", "-q", "-p", "no:cacheprovider"),
                _module("coverage", "combine", "-q"),
                _module("coverage", "report"),
            ),
        ),
    ]


def run_command(command: Sequence[str], cwd: Path) -> tuple[int, str]:
    """Run one command and return its exit code and combined output."""
    result = subprocess.run(list(command), cwd=cwd, capture_output=True, text=True, check=False)
    return result.returncode, result.stdout + result.stderr


def run_step(step: Step, root: Path, runner: Runner = run_command) -> Outcome:
    """Run a step's commands until one fails; a step with no command is skipped."""
    if not step.commands:
        return Outcome(step.name, "skip", 0.0, "")
    start = time.perf_counter()
    outputs = []
    for command in step.commands:
        code, output = runner(command, root)
        outputs.append(output)
        if code != 0:
            return Outcome(step.name, "FAIL", time.perf_counter() - start, "".join(outputs))
    return Outcome(step.name, "pass", time.perf_counter() - start, "".join(outputs))


def base_ref(root: Path) -> str | None:
    """Return the ref to compare against for docs sync, or None outside a usable checkout."""
    for ref in BASE_REFS:
        code, _ = run_command(("git", "rev-parse", "--verify", "--quiet", ref), root)
        if code == 0:
            return ref
    return None


def render(outcomes: Sequence[Outcome]) -> str:
    """Render the outcomes as a Markdown table followed by the output of every failure."""
    width = max(len(o.name) for o in outcomes)
    lines = [
        f"| {'Check':<{width}} | Result | Seconds |",
        f"|{'-' * (width + 2)}|--------|---------|",
    ]
    lines += [f"| {o.name:<{width}} | {o.status:<6} | {o.seconds:7.1f} |" for o in outcomes]
    for outcome in outcomes:
        if outcome.status == "FAIL":
            lines += ["", f"--- {outcome.name} ---", outcome.output.rstrip()]
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    """Run the selected gates and return 1 if any failed."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--only", action="append", metavar="NAME", help="run only this step")
    parser.add_argument("--list", action="store_true", help="list the steps and exit")
    args = parser.parse_args(argv)
    root = repo_root()
    selected = steps(base_ref(root))
    if args.list:
        print("\n".join(step.name for step in selected))
        return 0
    if args.only:
        unknown = set(args.only) - {step.name for step in selected}
        if unknown:
            parser.error(f"unknown step(s): {', '.join(sorted(unknown))}")
        selected = [step for step in selected if step.name in args.only]
    outcomes = [run_step(step, root) for step in selected]
    print(render(outcomes))
    return 1 if any(o.status == "FAIL" for o in outcomes) else 0


if __name__ == "__main__":
    sys.exit(main())
