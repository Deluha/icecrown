"""The convention checker, C1 to C7, on small synthetic packages."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

import check_conventions as cc
from _toolkit import repo_root

if TYPE_CHECKING:
    from pathlib import Path

PYPROJECT = """
[project]
name = "icecrown"
scripts = { icecrown = "icecrown.__main__:main" }

[project.entry-points.pytest11]
icecrown = "icecrown.pytest_plugin"
"""

INIT = '''"""Package."""

from icecrown._api import freeze

__version__ = "1"
"""The version."""

__all__ = ["__version__", "freeze"]
'''

API = '''"""API."""


def freeze() -> None:
    """Freeze."""
'''


def make_repo(tmp_path: Path, files: dict[str, str] | None = None) -> Path:
    base = {
        "pyproject.toml": PYPROJECT,
        "src/icecrown/__init__.py": INIT,
        "src/icecrown/_api.py": API,
        "tests/test_x.py": "",
    }
    for rel, text in {**base, **(files or {})}.items():
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return tmp_path


def codes(root: Path) -> list[str]:
    return [f"{v.code}:{v.path}" for v in cc.check(root)]


def test_clean_package_passes(tmp_path: Path) -> None:
    assert cc.check(make_repo(tmp_path)) == []


def test_c1_print_and_std_streams_outside_messages(tmp_path: Path) -> None:
    root = make_repo(
        tmp_path,
        {
            "src/icecrown/_a.py": "import sys\nprint(1)\nsys.stdout.write('x')\n",
            "src/icecrown/_b.py": "from sys import stderr\n",
            "src/icecrown/_messages.py": "import sys\nprint(1)\nsys.stderr.write('x')\n",
        },
    )
    assert codes(root) == ["C1:src/icecrown/_a.py"] * 2 + ["C1:src/icecrown/_b.py"]


def test_c1_sees_through_aliases_and_original_streams(tmp_path: Path) -> None:
    root = make_repo(
        tmp_path, {"src/icecrown/_a.py": "import sys as s\ns.stdout.write('x')\nsys.__stderr__\n"}
    )
    assert codes(root) == ["C1:src/icecrown/_a.py"] * 2


@pytest.mark.parametrize(
    "source",
    [
        "import time\n",
        "import os.path\n",
        "from random import random\n",
        "x = hash('a')\n",
        "import datetime\nx = datetime.datetime.now()\n",
        "from datetime import date\nx = date.today()\n",
    ],
)
def test_c2_nondeterminism_in_the_fingerprint_path(tmp_path: Path, source: str) -> None:
    root = make_repo(tmp_path, {"src/icecrown/_canon.py": source})
    assert codes(root) == ["C2:src/icecrown/_canon.py"]


def test_c2_covers_a_fingerprint_subpackage(tmp_path: Path) -> None:
    root = make_repo(tmp_path, {"src/icecrown/_canon/helpers.py": "import time\n"})
    assert codes(root) == ["C2:src/icecrown/_canon/helpers.py"]


def test_c2_applies_only_to_the_fingerprint_path(tmp_path: Path) -> None:
    root = make_repo(tmp_path, {"src/icecrown/_store.py": "import os\nimport time\n"})
    assert cc.check(root) == []


@pytest.mark.parametrize(
    "source",
    [
        "import socket\n",
        "from urllib import request\n",
        "import http.client\n",
        "import requests\n",
    ],
)
def test_c3_network_imports(tmp_path: Path, source: str) -> None:
    root = make_repo(tmp_path, {"src/icecrown/_x.py": source})
    assert codes(root) == ["C3:src/icecrown/_x.py"]


def test_c3_allows_harmless_neighbours(tmp_path: Path) -> None:
    root = make_repo(
        tmp_path, {"src/icecrown/_x.py": "import urllib.parse\nfrom http import HTTPStatus\n"}
    )
    assert cc.check(root) == []


def test_c4_public_modules_need_an_entry_point(tmp_path: Path) -> None:
    root = make_repo(
        tmp_path,
        {
            "src/icecrown/helpers.py": "",
            "src/icecrown/pytest_plugin.py": "",
            "src/icecrown/__main__.py": "",
            "src/icecrown/public_pkg/__init__.py": "",
            "src/icecrown/_private_pkg/__init__.py": "",
        },
    )
    assert codes(root) == ["C4:src/icecrown/helpers.py", "C4:src/icecrown/public_pkg"]


def test_c4_entry_point_functions_stay_short(tmp_path: Path) -> None:
    long_body = "".join(f"    x{i} = {i}\n" for i in range(cc.ENTRY_POINT_MAX_LINES))
    root = make_repo(
        tmp_path,
        {
            "src/icecrown/__main__.py": f"def main() -> None:\n{long_body}",
            "src/icecrown/_logic.py": f"def long() -> None:\n{long_body}",
        },
    )
    assert codes(root) == ["C4:src/icecrown/__main__.py"]


def test_c4_entry_point_packages(tmp_path: Path) -> None:
    long_body = "".join(f"    x{i} = {i}\n" for i in range(cc.ENTRY_POINT_MAX_LINES))
    pyproject = PYPROJECT.replace("icecrown.__main__:main", "icecrown.cli:main")
    root = make_repo(
        tmp_path,
        {
            "pyproject.toml": pyproject,
            "src/icecrown/cli/__init__.py": f"def main() -> None:\n{long_body}",
        },
    )
    assert [v.message.split(" is ")[0] for v in cc.check(root)] == ["entry-point function main()"]


def test_c5_test_files_outside_tests(tmp_path: Path) -> None:
    root = make_repo(tmp_path, {"tools/test_tool.py": "", "conftest.py": "", "src/a_test.py": ""})
    assert sorted(codes(root)) == ["C5:conftest.py", "C5:src/a_test.py", "C5:tools/test_tool.py"]


def test_c6_version_constants_only_in_the_registry(tmp_path: Path) -> None:
    root = make_repo(
        tmp_path,
        {
            "src/icecrown/_versions.py": "STORE_FORMAT_VERSION = 1\n",
            "src/icecrown/_store.py": "SPEC_VERSION: int = 1\n__version__ = 'x'\n",
            "src/icecrown/_other.py": (
                "A_VERSION, B = 1, 2\nif True:\n    C_VERSION = 3\n"
                "try:\n    pass\nexcept ImportError:\n    D_VERSION = 4\n"
                "def f() -> None:\n    LOCAL_VERSION = 5\n"
            ),
        },
    )
    assert sorted(v.message.split()[0] for v in cc.check(root)) == [
        "A_VERSION",
        "C_VERSION",
        "D_VERSION",
        "SPEC_VERSION",
    ]


def test_c7_missing_all(tmp_path: Path) -> None:
    root = make_repo(tmp_path, {"src/icecrown/__init__.py": '"""Package."""\n'})
    assert codes(root) == ["C7:src/icecrown/__init__.py"]


def test_c7_undefined_and_undocumented_names(tmp_path: Path) -> None:
    init = (
        '"""P."""\nfrom icecrown._api import freeze\n\nVALUE = 1\n\ndef f() -> None:\n    pass\n\n'
        '__all__ = ["VALUE", "f", "freeze", "ghost"]\n'
    )
    root = make_repo(
        tmp_path,
        {
            "src/icecrown/__init__.py": init,
            "src/icecrown/_api.py": "def freeze() -> None:\n    pass\n",
        },
    )
    messages = sorted(v.message for v in cc.check(root))
    assert messages == [
        "'VALUE' has no docstring",
        "'f' has no docstring",
        "'freeze' has no docstring",
        "'ghost' is in __all__ but not defined",
    ]


def test_c7_accepts_an_imported_module(tmp_path: Path) -> None:
    init = (
        INIT.replace('"freeze"]', '"freeze", "sources"]') + "import icecrown._sources as sources\n"
    )
    root = make_repo(tmp_path, {"src/icecrown/__init__.py": init})
    assert cc.check(root) == []


def test_entry_points_are_read_from_pyproject(tmp_path: Path) -> None:
    assert cc.declared_entry_points(make_repo(tmp_path)) == {"__main__", "pytest_plugin"}


def test_the_repository_itself_passes() -> None:
    assert cc.check(repo_root()) == []
