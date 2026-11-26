"""The installed package: version, typing marker and public names."""

from importlib.metadata import version
from importlib.resources import files

import icecrown


def test_version_comes_from_the_distribution_metadata() -> None:
    assert icecrown.__version__ == version("icecrown")


def test_package_ships_the_typing_marker() -> None:
    assert files("icecrown").joinpath("py.typed").is_file()


def test_public_names_are_declared_and_present() -> None:
    for name in icecrown.__all__:
        assert hasattr(icecrown, name)
