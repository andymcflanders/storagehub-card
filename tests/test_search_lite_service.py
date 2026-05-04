"""Tests for the storagehub.search_lite and storagehub.refresh_index services.

Note: tests that go through async_setup_component must stub /api/ha/items/index
because IndexCoordinator's first refresh runs during config-entry setup. The
"before first refresh" path doesn't have a real test fixture: if the index
fetch fails at setup, the entry never loads, so async_loaded_entries() returns
empty and not_configured fires — covered by test_search_lite_not_configured.
"""

from __future__ import annotations

from typing import Any

import pytest
from homeassistant.const import CONF_API_KEY, CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ServiceValidationError
from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.test_util.aiohttp import (
    AiohttpClientMocker,
)

from custom_components.storagehub.const import DOMAIN

HOST = "http://example.test"
API_KEY = "shub_test"


def _stub_status(mock: AiohttpClientMocker) -> None:
    mock.get(
        f"{HOST}/api/ha/status",
        json={"name": "StorageHub", "version": "1.1.0", "api_version": "v1"},
    )
    mock.get(f"{HOST}/api/ha/stats", json={"total_items": 5})


def _index_payload() -> list[dict[str, Any]]:
    return [
        {
            "id": "abc",
            "name": "Blå Cordbukser",
            "owner_name": "Sverre",
            "container_name": "Kasse 1",
            "location_name": "Sportsbod",
            "ai_names": ["Blue Cord Pants"],
        },
        {
            "id": "def",
            "name": "Apple TV Fjernkontroll",
            "owner_name": None,
            "container_name": None,
            "location_name": None,
            "ai_names": [],
        },
    ]


async def _setup_integration(
    hass: HomeAssistant,
    aioclient_mock: AiohttpClientMocker,
    *,
    etag: str = '"v1"',
) -> MockConfigEntry:
    _stub_status(aioclient_mock)
    aioclient_mock.get(
        f"{HOST}/api/ha/items/index",
        json=_index_payload(),
        headers={"ETag": etag},
    )
    entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id=HOST,
        data={CONF_HOST: HOST, CONF_API_KEY: API_KEY},
    )
    entry.add_to_hass(hass)
    assert await async_setup_component(hass, DOMAIN, {})
    await hass.async_block_till_done()
    return entry


async def _setup_only(hass: HomeAssistant) -> None:
    """async_setup runs (services register), but no config entry exists."""
    assert await async_setup_component(hass, DOMAIN, {})
    await hass.async_block_till_done()


async def test_services_registered_after_setup(hass: HomeAssistant) -> None:
    await _setup_only(hass)
    assert hass.services.has_service(DOMAIN, "search_lite")
    assert hass.services.has_service(DOMAIN, "refresh_index")


async def test_search_lite_returns_cached_payload(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    await _setup_integration(hass, aioclient_mock)

    response = await hass.services.async_call(
        DOMAIN, "search_lite", {}, blocking=True, return_response=True
    )

    assert response is not None
    assert response["etag"] == '"v1"'
    assert response["count"] == 2
    assert len(response["items"]) == 2
    first = response["items"][0]
    assert first["id"] == "abc"
    assert first["owner_name"] == "Sverre"
    assert first["ai_names"] == ["Blue Cord Pants"]
    # Lite shape only — no description / value_estimate / etc.
    assert set(first.keys()) == {
        "id",
        "name",
        "owner_name",
        "container_name",
        "location_name",
        "ai_names",
    }


async def test_search_lite_not_configured(hass: HomeAssistant) -> None:
    await _setup_only(hass)

    with pytest.raises(ServiceValidationError) as exc_info:
        await hass.services.async_call(
            DOMAIN, "search_lite", {}, blocking=True, return_response=True
        )

    assert exc_info.value.translation_key == "not_configured"


async def test_refresh_index_picks_up_new_etag(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    await _setup_integration(hass, aioclient_mock, etag='"v1"')

    aioclient_mock.clear_requests()
    aioclient_mock.get(
        f"{HOST}/api/ha/items/index",
        json=_index_payload(),
        headers={"ETag": '"v2"'},
    )

    await hass.services.async_call(DOMAIN, "refresh_index", {}, blocking=True)
    await hass.async_block_till_done()

    response = await hass.services.async_call(
        DOMAIN, "search_lite", {}, blocking=True, return_response=True
    )
    assert response is not None
    assert response["etag"] == '"v2"'


async def test_refresh_index_not_configured(hass: HomeAssistant) -> None:
    await _setup_only(hass)

    with pytest.raises(ServiceValidationError) as exc_info:
        await hass.services.async_call(DOMAIN, "refresh_index", {}, blocking=True)

    assert exc_info.value.translation_key == "not_configured"
