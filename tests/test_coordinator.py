"""Tests for the StorageHub IndexCoordinator."""

from __future__ import annotations

import aiohttp
import pytest
from homeassistant.const import CONF_API_KEY, CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.test_util.aiohttp import (
    AiohttpClientMocker,
)

from custom_components.storagehub.api import StorageHubApiClient
from custom_components.storagehub.const import DOMAIN
from custom_components.storagehub.coordinator import IndexCoordinator

HOST = "http://example.test"
API_KEY = "shub_test"


def _make_coordinator(hass: HomeAssistant) -> IndexCoordinator:
    entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id=HOST,
        data={CONF_HOST: HOST, CONF_API_KEY: API_KEY},
    )
    entry.add_to_hass(hass)
    client = StorageHubApiClient(
        session=async_get_clientsession(hass), host=HOST, api_key=API_KEY
    )
    return IndexCoordinator(hass, client, entry)


_BODY = [
    {
        "id": "abc",
        "name": "Bukser",
        "owner_name": "Sverre",
        "container_name": "Kasse 1",
        "location_name": "Sportsbod",
        "ai_names": [],
    }
]


async def test_first_refresh_populates_data(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    aioclient_mock.get(
        f"{HOST}/api/ha/items/index", json=_BODY, headers={"ETag": '"v1"'}
    )

    coordinator = _make_coordinator(hass)
    await coordinator.async_refresh()

    assert coordinator.data is not None
    assert coordinator.data.etag == '"v1"'
    assert len(coordinator.data.entries) == 1
    assert coordinator.data.entries[0].id == "abc"


async def test_304_retains_prior_data(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    # PHCC's mocker doesn't have a request-count side_effect, so we run the
    # 200-then-304 sequence by clearing and re-registering between refreshes.
    aioclient_mock.get(
        f"{HOST}/api/ha/items/index", json=_BODY, headers={"ETag": '"v1"'}
    )
    coordinator = _make_coordinator(hass)
    await coordinator.async_refresh()
    first_data = coordinator.data
    assert first_data is not None

    aioclient_mock.clear_requests()
    aioclient_mock.get(f"{HOST}/api/ha/items/index", status=304)

    await coordinator.async_refresh()
    assert coordinator.last_update_success is True
    assert coordinator.data is first_data  # same identity — no rebuild


async def test_auth_failure_raises_config_entry_auth_failed(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    aioclient_mock.get(f"{HOST}/api/ha/items/index", status=401)

    coordinator = _make_coordinator(hass)
    with pytest.raises(ConfigEntryAuthFailed):
        await coordinator._async_update_data()


async def test_network_error_marks_unavailable(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    # Prime with a successful first refresh so subsequent failures don't
    # raise ConfigEntryNotReady (that's the first-refresh-only path).
    aioclient_mock.get(
        f"{HOST}/api/ha/items/index", json=_BODY, headers={"ETag": '"v1"'}
    )
    coordinator = _make_coordinator(hass)
    await coordinator.async_refresh()

    aioclient_mock.clear_requests()
    aioclient_mock.get(
        f"{HOST}/api/ha/items/index",
        exc=aiohttp.ClientConnectionError("network"),
    )

    await coordinator.async_refresh()
    assert coordinator.last_update_success is False
