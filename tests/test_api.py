"""Unit tests for the StorageHub API client."""

from __future__ import annotations

import aiohttp
import pytest
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from pytest_homeassistant_custom_component.test_util.aiohttp import (
    AiohttpClientMocker,
)

from custom_components.storagehub.api import (
    CannotConnect,
    InvalidAuth,
    StorageHubApiClient,
)

HOST = "http://example.test"
API_KEY = "shub_test"


def _client(hass: HomeAssistant) -> StorageHubApiClient:
    return StorageHubApiClient(
        session=async_get_clientsession(hass),
        host=HOST,
        api_key=API_KEY,
    )


async def test_get_status_no_auth_required(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    aioclient_mock.get(
        f"{HOST}/api/ha/status",
        json={"name": "StorageHub", "version": "1.1.0", "api_version": "v1"},
    )
    status = await _client(hass).async_get_status()
    assert status.name == "StorageHub"
    assert status.version == "1.1.0"
    assert status.instance_id is None


async def test_get_status_passes_through_instance_id(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    aioclient_mock.get(
        f"{HOST}/api/ha/status",
        json={
            "name": "StorageHub",
            "version": "1.1.0",
            "api_version": "v1",
            "instance_id": "abc-123",
        },
    )
    status = await _client(hass).async_get_status()
    assert status.instance_id == "abc-123"


async def test_get_stats(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    aioclient_mock.get(f"{HOST}/api/ha/stats", json={"total_items": 42})
    stats = await _client(hass).async_get_stats()
    assert stats.total_items == 42


async def test_invalid_auth(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    aioclient_mock.get(f"{HOST}/api/ha/stats", status=401)
    with pytest.raises(InvalidAuth):
        await _client(hass).async_get_stats()


async def test_forbidden_is_invalid_auth(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    aioclient_mock.get(f"{HOST}/api/ha/stats", status=403)
    with pytest.raises(InvalidAuth):
        await _client(hass).async_get_stats()


async def test_cannot_connect(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    aioclient_mock.get(
        f"{HOST}/api/ha/status",
        exc=aiohttp.ClientConnectionError("boom"),
    )
    with pytest.raises(CannotConnect):
        await _client(hass).async_get_status()


async def test_strips_trailing_slash_from_host(hass: HomeAssistant) -> None:
    client = StorageHubApiClient(
        session=async_get_clientsession(hass),
        host="http://example.test/",
        api_key=API_KEY,
    )
    assert client.host == "http://example.test"
