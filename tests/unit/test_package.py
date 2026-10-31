"""Smoke test: the package is importable and exposes its version."""

from az_voice_operator import __version__


def test_package_version_is_defined() -> None:
    assert isinstance(__version__, str)
    assert __version__
