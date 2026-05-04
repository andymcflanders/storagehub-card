"""Shared pytest fixtures for the StorageHub integration tests."""

from __future__ import annotations

import pycares
import pytest
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component

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


@pytest.fixture(autouse=True)
async def _bring_up_homeassistant(hass: HomeAssistant) -> None:
    """Set up the `homeassistant` core component for every test.

    The integration declares `conversation` as a manifest dependency
    (phase 2 voice trigger), and `conversation`'s default agent walks
    the exposed-entities table that `homeassistant` core populates.
    Bringing it up here keeps the per-test setup boilerplate small.
    """
    assert await async_setup_component(hass, "homeassistant", {})
