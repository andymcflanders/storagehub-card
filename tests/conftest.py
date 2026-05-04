"""Shared pytest fixtures for the StorageHub integration tests."""

from __future__ import annotations

import pycares
import pytest

pytest_plugins = ["pytest_homeassistant_custom_component"]

# pycares spins up a daemon shutdown thread the first time a Channel is
# created. Without pre-warming, HA's verify_cleanup fails the first test on a
# "lingering thread" because that thread didn't exist when it snapshotted
# threads_before. Creating a Channel at import time lands the thread before
# any test starts.
_PYCARES_PREWARM = pycares.Channel()


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations: None) -> None:
    """Make HA load `custom_components/storagehub` for every test."""
    return None
