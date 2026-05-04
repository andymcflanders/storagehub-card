"""Tests for the storagehub.search service."""

from __future__ import annotations

from typing import Any

import aiohttp
import pytest
import voluptuous as vol
from homeassistant.const import CONF_API_KEY, CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
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


def _search_payload(
    items: list[dict[str, Any]] | None = None, query: str = "Sverre"
) -> dict[str, Any]:
    items = items if items is not None else [_sample_item()]
    return {"items": items, "total_count": len(items), "query": query}


def _sample_item(**overrides: Any) -> dict[str, Any]:
    base = {
        "id": "abc-123",
        "name": "Blå Cordbukser",
        "description": "H&M",
        "container_name": "Kasse 1",
        "location_name": "Sportsbod",
        "condition": "good",
        "seasonal": "winter",
        "value_estimate": 199.0,
        "owner_name": "Sverre",
        "primary_image_url": "/uploads/x.jpg",
        "tags": ["clothing", "winter"],
    }
    base.update(overrides)
    return base


async def _setup_integration(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> MockConfigEntry:
    _stub_status(aioclient_mock)
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
    """Run async_setup without any config entry."""
    assert await async_setup_component(hass, DOMAIN, {})
    await hass.async_block_till_done()


async def test_service_registered_after_setup(hass: HomeAssistant) -> None:
    await _setup_only(hass)
    assert hass.services.has_service(DOMAIN, "search")


async def test_search_happy_path(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    await _setup_integration(hass, aioclient_mock)
    aioclient_mock.get(f"{HOST}/api/ha/search", json=_search_payload())

    response = await hass.services.async_call(
        DOMAIN,
        "search",
        {"query": "Sverre Bukser"},
        blocking=True,
        return_response=True,
    )

    assert response is not None
    assert response["total_count"] == 1
    assert response["query"] == "Sverre"
    assert len(response["items"]) == 1
    item = response["items"][0]
    assert item["id"] == "abc-123"
    assert item["owner_name"] == "Sverre"
    assert item["value_estimate"] == 199.0
    assert item["tags"] == ["clothing", "winter"]
    assert set(item.keys()) == {
        "id",
        "name",
        "description",
        "container_name",
        "location_name",
        "condition",
        "seasonal",
        "value_estimate",
        "owner_name",
        "primary_image_url",
        "tags",
    }


async def test_search_default_limit_is_20(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    await _setup_integration(hass, aioclient_mock)
    aioclient_mock.get(f"{HOST}/api/ha/search", json=_search_payload([]))

    await hass.services.async_call(
        DOMAIN, "search", {"query": "anything"}, blocking=True, return_response=True
    )

    request = aioclient_mock.mock_calls[-1]
    assert request[1].query["limit"] == "20"


async def test_search_respects_custom_limit(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    await _setup_integration(hass, aioclient_mock)
    aioclient_mock.get(f"{HOST}/api/ha/search", json=_search_payload([]))

    await hass.services.async_call(
        DOMAIN,
        "search",
        {"query": "anything", "limit": 7},
        blocking=True,
        return_response=True,
    )

    request = aioclient_mock.mock_calls[-1]
    assert request[1].query["limit"] == "7"


async def test_search_empty_results(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    await _setup_integration(hass, aioclient_mock)
    aioclient_mock.get(
        f"{HOST}/api/ha/search",
        json={"items": [], "total_count": 0, "query": "nothing"},
    )

    response = await hass.services.async_call(
        DOMAIN,
        "search",
        {"query": "nothing"},
        blocking=True,
        return_response=True,
    )

    assert response == {"items": [], "total_count": 0, "query": "nothing"}


async def test_search_rejects_short_query(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    await _setup_integration(hass, aioclient_mock)
    initial_calls = len(aioclient_mock.mock_calls)

    with pytest.raises(vol.Invalid):
        await hass.services.async_call(
            DOMAIN, "search", {"query": "a"}, blocking=True, return_response=True
        )

    assert len(aioclient_mock.mock_calls) == initial_calls


async def test_search_rejects_limit_out_of_range(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    await _setup_integration(hass, aioclient_mock)

    for bad_limit in (0, 51):
        with pytest.raises(vol.Invalid):
            await hass.services.async_call(
                DOMAIN,
                "search",
                {"query": "valid", "limit": bad_limit},
                blocking=True,
                return_response=True,
            )


async def test_search_auth_failure(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    await _setup_integration(hass, aioclient_mock)
    aioclient_mock.get(f"{HOST}/api/ha/search", status=401)

    with pytest.raises(HomeAssistantError) as exc_info:
        await hass.services.async_call(
            DOMAIN, "search", {"query": "valid"}, blocking=True, return_response=True
        )

    assert not isinstance(exc_info.value, ServiceValidationError)
    assert exc_info.value.translation_key == "auth_failed"
    assert exc_info.value.translation_domain == DOMAIN


async def test_search_connection_failure(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    await _setup_integration(hass, aioclient_mock)
    aioclient_mock.get(
        f"{HOST}/api/ha/search", exc=aiohttp.ClientConnectionError("boom")
    )

    with pytest.raises(HomeAssistantError) as exc_info:
        await hass.services.async_call(
            DOMAIN, "search", {"query": "valid"}, blocking=True, return_response=True
        )

    assert exc_info.value.translation_key == "cannot_connect"


async def test_search_api_error_passes_detail(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    await _setup_integration(hass, aioclient_mock)
    aioclient_mock.get(f"{HOST}/api/ha/search", status=500, text="boom")

    with pytest.raises(HomeAssistantError) as exc_info:
        await hass.services.async_call(
            DOMAIN, "search", {"query": "valid"}, blocking=True, return_response=True
        )

    assert exc_info.value.translation_key == "api_error"
    assert "detail" in exc_info.value.translation_placeholders
    assert exc_info.value.translation_placeholders["detail"]


async def test_search_not_configured(hass: HomeAssistant) -> None:
    await _setup_only(hass)

    with pytest.raises(ServiceValidationError) as exc_info:
        await hass.services.async_call(
            DOMAIN, "search", {"query": "valid"}, blocking=True, return_response=True
        )

    assert exc_info.value.translation_key == "not_configured"


async def test_search_survives_entry_reload(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    entry = await _setup_integration(hass, aioclient_mock)

    await hass.config_entries.async_reload(entry.entry_id)
    await hass.async_block_till_done()

    aioclient_mock.get(f"{HOST}/api/ha/search", json=_search_payload())

    response = await hass.services.async_call(
        DOMAIN, "search", {"query": "Sverre"}, blocking=True, return_response=True
    )
    assert response is not None
    assert response["total_count"] == 1
