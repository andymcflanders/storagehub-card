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
from yarl import URL

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


async def test_search_passes_query_and_limit(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    aioclient_mock.get(
        f"{HOST}/api/ha/search",
        json={"items": [], "total_count": 0, "query": "Sverre Bukser"},
    )
    await _client(hass).async_search("Sverre Bukser", limit=5)

    request = aioclient_mock.mock_calls[-1]
    url: URL = request[1]
    assert url.query["q"] == "Sverre Bukser"
    assert url.query["limit"] == "5"


async def test_search_parses_response(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    aioclient_mock.get(
        f"{HOST}/api/ha/search",
        json={
            "items": [
                {
                    "id": "abc",
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
            ],
            "total_count": 1,
            "query": "Sverre",
        },
    )
    result = await _client(hass).async_search("Sverre")
    assert result.total_count == 1
    assert result.query == "Sverre"
    assert len(result.items) == 1
    item = result.items[0]
    assert item.id == "abc"
    assert item.owner_name == "Sverre"
    assert item.value_estimate == 199.0
    assert item.tags == ("clothing", "winter")


async def test_search_invalid_auth(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    aioclient_mock.get(f"{HOST}/api/ha/search", status=401)
    with pytest.raises(InvalidAuth):
        await _client(hass).async_search("Sverre")


_INDEX_BODY = [
    {
        "id": "abc",
        "name": "Blå Cordbukser",
        "owner_name": "Sverre",
        "container_name": "Kasse 1",
        "location_name": "Sportsbod",
        "ai_names": ["Blue Cord Pants", "Blå Cordbukser"],
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


async def test_get_index_first_fetch_omits_if_none_match(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    aioclient_mock.get(
        f"{HOST}/api/ha/items/index",
        json=_INDEX_BODY,
        headers={"ETag": '"abc123"'},
    )

    etag, entries = await _client(hass).async_get_index()

    assert etag == '"abc123"'
    assert entries is not None and len(entries) == 2
    request = aioclient_mock.mock_calls[-1]
    headers = request[3]
    assert "If-None-Match" not in headers


async def test_get_index_sends_if_none_match_and_handles_304(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    aioclient_mock.get(f"{HOST}/api/ha/items/index", status=304)

    etag, entries = await _client(hass).async_get_index(etag='"abc123"')

    assert etag == '"abc123"'  # request etag passes through unchanged
    assert entries is None
    request = aioclient_mock.mock_calls[-1]
    headers = request[3]
    assert headers["If-None-Match"] == '"abc123"'


async def test_get_index_parses_entries(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    aioclient_mock.get(
        f"{HOST}/api/ha/items/index",
        json=_INDEX_BODY,
        headers={"ETag": '"x"'},
    )

    _, entries = await _client(hass).async_get_index()
    assert entries is not None
    first, second = entries
    assert first.id == "abc"
    assert first.owner_name == "Sverre"
    assert first.ai_names == ("Blue Cord Pants", "Blå Cordbukser")
    assert second.owner_name is None
    assert second.container_name is None
    assert second.ai_names == ()


async def test_get_index_invalid_auth(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    aioclient_mock.get(f"{HOST}/api/ha/items/index", status=401)
    with pytest.raises(InvalidAuth):
        await _client(hass).async_get_index()


async def test_get_index_cannot_connect(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    aioclient_mock.get(
        f"{HOST}/api/ha/items/index",
        exc=aiohttp.ClientConnectionError("boom"),
    )
    with pytest.raises(CannotConnect):
        await _client(hass).async_get_index()
