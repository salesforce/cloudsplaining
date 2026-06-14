"""Shared pytest fixtures for the cloudsplaining test suite."""

import pytest

from cloudsplaining.shared.exclusions import set_exclusion_output


@pytest.fixture(autouse=True)
def _reset_exclusion_output():
    """Reset the exclusion-output toggle to the library default after every test.

    The CLI scopes ``set_exclusion_output(True)`` to its invocation and restores it on
    teardown, so this is defense-in-depth: it guarantees that any test which flips the
    toggle directly (or a CLI test that bypasses normal context teardown) cannot leak
    printing state into another test and cause order-dependent flakiness.
    """
    yield
    set_exclusion_output(False)
