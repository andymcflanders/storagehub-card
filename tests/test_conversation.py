"""Tests for the StorageHub voice/Assist trigger."""

from __future__ import annotations

from typing import Any

import aiohttp
from homeassistant.components.conversation import async_converse
from homeassistant.const import CONF_API_KEY, CONF_HOST
from homeassistant.core import Context, HomeAssistant
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


def _item(**overrides: Any) -> dict[str, Any]:
    base = {
        "id": "abc",
        "name": "yellow rain jacket",
        "description": None,
        "container_name": "Winter",
        "location_name": "Attic",
        "condition": "good",
        "seasonal": "winter",
        "value_estimate": None,
        "owner_name": None,
        "primary_image_url": None,
        "tags": [],
    }
    base.update(overrides)
    return base


async def _setup_full(
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


async def _say(hass: HomeAssistant, text: str, language: str = "en") -> str:
    result = await async_converse(
        hass, text, conversation_id=None, context=Context(), language=language
    )
    return result.response.speech["plain"]["speech"]


async def test_register_trigger_attaches_after_setup(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    await _setup_full(hass, aioclient_mock)
    from homeassistant.components.conversation.const import DATA_DEFAULT_ENTITY

    agent = hass.data[DATA_DEFAULT_ENTITY]
    assert any(
        any("{item}" in s for s in trigger.sentences)
        for trigger in agent.trigger_sentences
    )


async def test_voice_happy_path_with_owner_en(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    await _setup_full(hass, aioclient_mock)
    aioclient_mock.get(
        f"{HOST}/api/ha/search",
        json={
            "items": [_item(name="rain jacket", owner_name="Sverre")],
            "total_count": 1,
            "query": "Sverre's jacket",
        },
    )

    speech = await _say(hass, "where is Sverre's jacket")
    assert speech == "Sverre's rain jacket is in the Winter box in the Attic."

    request = aioclient_mock.mock_calls[-1]
    assert request[1].query["q"] == "Sverre's jacket"


async def test_voice_happy_path_no_owner_en(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    await _setup_full(hass, aioclient_mock)
    aioclient_mock.get(
        f"{HOST}/api/ha/search",
        json={"items": [_item()], "total_count": 1, "query": "yellow jacket"},
    )

    speech = await _say(hass, "where is the yellow jacket")
    assert speech == "The yellow rain jacket is in the Winter box in the Attic."


async def test_voice_norwegian_possessive(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    await _setup_full(hass, aioclient_mock)
    aioclient_mock.get(
        f"{HOST}/api/ha/search",
        json={
            "items": [
                _item(
                    name="rød ullgenser",
                    owner_name="Sverre",
                    container_name="Vinter",
                    location_name="loftet",
                )
            ],
            "total_count": 1,
            "query": "Sverres ullgenser",
        },
    )

    speech = await _say(hass, "hvor er Sverres ullgenser", language="no")
    assert speech == "Sverres rød ullgenser ligger i boksen Vinter på loftet."


async def test_voice_no_results(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    await _setup_full(hass, aioclient_mock)
    aioclient_mock.get(
        f"{HOST}/api/ha/search",
        json={"items": [], "total_count": 0, "query": "foobar"},
    )

    speech = await _say(hass, "find foobar")
    assert speech == "I couldn't find a foobar in your inventory."


async def test_voice_multi_result_summary(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    await _setup_full(hass, aioclient_mock)
    aioclient_mock.get(
        f"{HOST}/api/ha/search",
        json={
            "items": [
                _item(name="red jacket", container_name="Winter"),
                _item(name="blue jacket", container_name="Summer"),
                _item(name="green jacket", container_name="Spring"),
            ],
            "total_count": 3,
            "query": "jacket",
        },
    )

    speech = await _say(hass, "find jacket")
    assert speech == "I found 3 matches: red jacket and blue jacket, and 1 more."


async def test_voice_multi_same_container_picks_top(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    await _setup_full(hass, aioclient_mock)
    aioclient_mock.get(
        f"{HOST}/api/ha/search",
        json={
            "items": [
                _item(name="red jacket", container_name="Winter"),
                _item(name="blue jacket", container_name="Winter"),
            ],
            "total_count": 2,
            "query": "jacket",
        },
    )

    speech = await _say(hass, "find jacket")
    assert speech == "The red jacket is in the Winter box in the Attic."


async def test_voice_cannot_connect(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    await _setup_full(hass, aioclient_mock)
    aioclient_mock.get(
        f"{HOST}/api/ha/search", exc=aiohttp.ClientConnectionError("boom")
    )

    speech = await _say(hass, "where is the bike")
    assert speech == "I couldn't reach StorageHub."


async def test_voice_invalid_auth(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    await _setup_full(hass, aioclient_mock)
    aioclient_mock.get(f"{HOST}/api/ha/search", status=401)

    speech = await _say(hass, "where is the bike")
    assert (
        speech == "StorageHub rejected my API key. Please reconfigure the integration."
    )


async def test_voice_not_configured(hass: HomeAssistant) -> None:
    assert await async_setup_component(hass, DOMAIN, {})
    await hass.async_block_till_done()

    speech = await _say(hass, "where is the bike")
    assert speech == "StorageHub isn't configured yet."


async def test_voice_unknown_sentence_pass_through(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    await _setup_full(hass, aioclient_mock)

    result = await async_converse(
        hass,
        "please order pizza",
        conversation_id=None,
        context=Context(),
        language="en",
    )
    # Default agent should NOT match our triggers and should report
    # no_intent_match (or similar). The exact response_type indicates an
    # error/no-match path; what matters is we didn't hit the trigger.
    assert result.response.error_code is not None
    assert len(aioclient_mock.mock_calls) == 2  # status + stats only
