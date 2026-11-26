"""Check the mechanical code conventions C1 to C7.

What each code means, and the hard rule behind it, is documented in
``.claude/skills/project-icecrown-development/references/checkers.md``.
"""

from __future__ import annotations

import argparse
import ast
import fnmatch
import sys
import tomllib
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING

from _toolkit import Violation, list_files, repo_root, report

if TYPE_CHECKING:
    from collections.abc import Iterator, Sequence

PACKAGE = "src/icecrown"
MESSAGES_MODULE = "_messages.py"
VERSIONS_MODULE = "_versions.py"
FINGERPRINT_PATH = frozenset({"_types.py", "_canon.py", "_fingerprint.py", "_soul.py"})
NONDETERMINISTIC_MODULES = frozenset(
    {"time", "random", "secrets", "uuid", "os", "platform", "locale", "getpass"}
)
NONDETERMINISTIC_BUILTINS = frozenset({"hash", "id"})
CLOCK_METHODS = frozenset({"now", "today", "utcnow"})
NETWORK_MODULES = frozenset(
    {
        "socket",
        "ssl",
        "http.client",
        "http.server",
        "urllib.request",
        "ftplib",
        "smtplib",
        "requests",
        "httpx",
        "aiohttp",
        "urllib3",
    }
)
ALWAYS_PUBLIC = frozenset({"__init__.py", "__main__.py"})
STD_STREAMS = frozenset({"stdout", "stderr", "__stdout__", "__stderr__"})
ENTRY_POINT_MAX_LINES = 40
MAX_REEXPORT_DEPTH = 3
TEST_FILE_PATTERNS = ("test_*.py", "*_test.py", "conftest.py")


def check(root: Path) -> list[Violation]:
    """Return every convention violation under ``root``."""
    violations: list[Violation] = []
    entry_points = declared_entry_points(root)
    for path in sorted((root / PACKAGE).rglob("*.py")):
        rel = path.relative_to(root).as_posix()
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=rel)
        inner = path.relative_to(root / PACKAGE)
        violations += check_output(rel, inner, tree)
        violations += check_determinism(rel, inner, tree)
        violations += check_network(rel, tree)
        violations += check_versions(rel, inner, tree)
        if Path(inner.parts[0]).stem in entry_points:
            violations += check_entry_point_length(rel, tree)
    violations += check_public_modules(root, entry_points)
    violations += check_test_locations(list_files(root))
    violations += check_public_api(root)
    return violations


def declared_entry_points(root: Path) -> frozenset[str]:
    """Return the top-level module names that ``pyproject.toml`` declares as entry points."""
    pyproject = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    project = pyproject.get("project", {})
    targets: list[str] = list(project.get("scripts", {}).values())
    targets += list(project.get("entry-points", {}).get("pytest11", {}).values())
    names = set()
    for target in targets:
        module = str(target).split(":", 1)[0].split(".")
        if module[0] == "icecrown" and len(module) > 1:
            names.add(module[1])
    return frozenset(names)


def _imported_modules(tree: ast.AST) -> Iterator[tuple[int, str, str]]:
    """Yield ``(line, module, full_name)`` for every absolute import.

    ``import a.b`` gives ``("a.b", "a.b")``; ``from a import b`` gives ``("a", "a.b")``.
    """
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                yield node.lineno, alias.name, alias.name
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            for alias in node.names:
                yield node.lineno, node.module, f"{node.module}.{alias.name}"


def _banned_prefix(name: str, banned: frozenset[str]) -> str | None:
    """Return the shortest dotted prefix of ``name`` that is in ``banned``, if any."""
    parts = name.split(".")
    return next(
        (".".join(parts[:i]) for i in range(1, len(parts) + 1) if ".".join(parts[:i]) in banned),
        None,
    )


def check_output(rel: str, inner: Path, tree: ast.AST) -> list[Violation]:
    """C1: console output only through the message helpers."""
    if inner.as_posix() == MESSAGES_MODULE:
        return []
    sys_names = {"sys"} | {
        alias.asname
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
        if alias.name == "sys" and alias.asname
    }
    found = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id == "print":
                found.append(Violation(rel, node.lineno, "C1", "print() outside the helpers"))
        elif (
            isinstance(node, ast.Attribute)
            and isinstance(node.value, ast.Name)
            and node.value.id in sys_names
            and node.attr in STD_STREAMS
        ):
            found.append(Violation(rel, node.lineno, "C1", f"sys.{node.attr} outside the helpers"))
        elif isinstance(node, ast.ImportFrom) and node.module == "sys":
            found.extend(
                Violation(rel, node.lineno, "C1", f"sys.{alias.name} outside the helpers")
                for alias in node.names
                if alias.name in STD_STREAMS
            )
    return found


def check_determinism(rel: str, inner: Path, tree: ast.AST) -> list[Violation]:
    """C2: nothing non-deterministic in a fingerprint-path module."""
    if f"{Path(inner.parts[0]).stem}.py" not in FINGERPRINT_PATH:
        return []
    found = [
        Violation(rel, line, "C2", f"import of {module!r} in the fingerprint path")
        for line, module, _ in _imported_modules(tree)
        if module.split(".")[0] in NONDETERMINISTIC_MODULES
    ]
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Name) and node.func.id in NONDETERMINISTIC_BUILTINS:
            found.append(Violation(rel, node.lineno, "C2", f"builtin {node.func.id}() call"))
        elif isinstance(node.func, ast.Attribute) and node.func.attr in CLOCK_METHODS:
            found.append(Violation(rel, node.lineno, "C2", f"clock call .{node.func.attr}()"))
    return sorted(set(found))


def check_network(rel: str, tree: ast.AST) -> list[Violation]:
    """C3: no network module anywhere in the package."""
    found = set()
    for line, _, full_name in _imported_modules(tree):
        banned = _banned_prefix(full_name, NETWORK_MODULES)
        if banned is not None:
            found.add(Violation(rel, line, "C3", f"network module {banned!r} imported"))
    return sorted(found)


def check_versions(rel: str, inner: Path, tree: ast.Module) -> list[Violation]:
    """C6: format-version constants are assigned only in the versions registry."""
    if inner.as_posix() == VERSIONS_MODULE:
        return []
    found: list[Violation] = []
    for node in _module_level(tree.body):
        targets: list[ast.expr] = []
        if isinstance(node, ast.Assign):
            targets = node.targets
        elif isinstance(node, ast.AnnAssign | ast.AugAssign):
            targets = [node.target]
        found.extend(
            Violation(rel, node.lineno, "C6", f"{name.id} assigned outside {VERSIONS_MODULE}")
            for target in targets
            for name in ast.walk(target)
            if isinstance(name, ast.Name)
            and isinstance(name.ctx, ast.Store)
            and name.id.endswith("_VERSION")
        )
    return found


def _module_level(body: Sequence[ast.stmt]) -> Iterator[ast.stmt]:
    """Yield the statements that run at module level, descending into if, try and with blocks."""
    for node in body:
        yield node
        if isinstance(node, ast.If | ast.With):
            yield from _module_level(node.body)
            yield from _module_level(getattr(node, "orelse", []))
        elif isinstance(node, ast.Try | ast.TryStar):
            for block in (node.body, node.orelse, node.finalbody):
                yield from _module_level(block)
            for handler in node.handlers:
                yield from _module_level(handler.body)


def check_entry_point_length(rel: str, tree: ast.AST) -> list[Violation]:
    """C4: every function in an entry-point module stays within the line budget."""
    found = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            length = (node.end_lineno or node.lineno) - node.lineno + 1
            if length > ENTRY_POINT_MAX_LINES:
                found.append(
                    Violation(
                        rel,
                        node.lineno,
                        "C4",
                        f"entry-point function {node.name}() is {length} lines "
                        f"(at most {ENTRY_POINT_MAX_LINES}); move logic to a private module",
                    )
                )
    return found


def check_public_modules(root: Path, entry_points: frozenset[str]) -> list[Violation]:
    """C4: every top-level module or package of ``icecrown`` is private unless it is allowed."""
    package = root / PACKAGE
    found = []
    for child in sorted(package.iterdir()):
        name = child.name
        if name.startswith(("_", ".")) or name in ALWAYS_PUBLIC:
            continue
        if child.is_dir() and not any(child.glob("*.py")):
            continue
        if child.stem in entry_points and (child.suffix == ".py" or child.is_dir()):
            continue
        if child.is_file() and child.suffix != ".py":
            continue
        rel = child.relative_to(root).as_posix()
        message = "public module; make it private (_name) or declare it as an entry point"
        found.append(Violation(rel, 1, "C4", message))
    return found


def check_test_locations(files: Sequence[str]) -> list[Violation]:
    """C5: test files live only under ``tests/``."""
    found = []
    for rel in files:
        path = PurePosixPath(rel)
        if path.parts[0] == "tests":
            continue
        if any(fnmatch.fnmatch(path.name, pattern) for pattern in TEST_FILE_PATTERNS):
            found.append(Violation(rel, 1, "C5", "test file outside tests/"))
    return found


def check_public_api(root: Path) -> list[Violation]:
    """C7: ``__all__`` is a literal list of defined, documented names."""
    init = root / PACKAGE / "__init__.py"
    rel = init.relative_to(root).as_posix()
    tree = ast.parse(init.read_text(encoding="utf-8"), filename=rel)
    names = _all_names(tree)
    if names is None:
        return [Violation(rel, 1, "C7", "__all__ is missing or not a literal list of strings")]
    found = []
    for line, name in names:
        documented = _has_docstring(root, tree, name, depth=0)
        if documented is None:
            found.append(Violation(rel, line, "C7", f"{name!r} is in __all__ but not defined"))
        elif not documented:
            found.append(Violation(rel, line, "C7", f"{name!r} has no docstring"))
    return found


def _all_names(tree: ast.Module) -> list[tuple[int, str]] | None:
    for node in tree.body:
        if (
            isinstance(node, ast.Assign | ast.AnnAssign)
            and any(
                isinstance(t, ast.Name) and t.id == "__all__"
                for t in (node.targets if isinstance(node, ast.Assign) else [node.target])
            )
            and isinstance(node.value, ast.List)
        ):
            items = node.value.elts
            if all(isinstance(i, ast.Constant) and isinstance(i.value, str) for i in items):
                return [(i.lineno, str(i.value)) for i in items if isinstance(i, ast.Constant)]
    return None


def _has_docstring(root: Path, tree: ast.Module, name: str, depth: int) -> bool | None:
    """Return whether ``name`` is documented where it is defined, or None if it is not defined."""
    body = tree.body
    for index, node in enumerate(body):
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef):
            if node.name == name:
                return ast.get_docstring(node) is not None
        elif isinstance(node, ast.Assign | ast.AnnAssign):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            if any(isinstance(t, ast.Name) and t.id == name for t in targets):
                following = body[index + 1] if index + 1 < len(body) else None
                return (
                    isinstance(following, ast.Expr)
                    and isinstance(following.value, ast.Constant)
                    and isinstance(following.value.value, str)
                )
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if (alias.asname or alias.name.split(".")[0]) == name:
                    return True  # a module: its own docstring is checked where it is defined
        elif isinstance(node, ast.ImportFrom) and node.module and depth < MAX_REEXPORT_DEPTH:
            for alias in node.names:
                if (alias.asname or alias.name) == name:
                    return _documented_in_module(root, node.module, alias.name, depth + 1)
    return None


def _documented_in_module(root: Path, module: str, name: str, depth: int) -> bool | None:
    parts = module.split(".")
    if parts[0] != "icecrown":
        return True  # a re-exported third-party name is documented upstream
    base = root / "src" / Path(*parts)
    source = base.with_suffix(".py") if base.with_suffix(".py").is_file() else base / "__init__.py"
    if not source.is_file():
        return None
    return _has_docstring(root, ast.parse(source.read_text(encoding="utf-8")), name, depth)


def main(argv: Sequence[str] | None = None) -> int:
    """Run the convention checks and return the exit code."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=repo_root(), help="repository root")
    args = parser.parse_args(argv)
    return report(check(args.root), "check_conventions")


if __name__ == "__main__":
    sys.exit(main())
