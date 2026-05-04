"""Config flow tests for the StorageHub integration."""

from __future__ import annotations

from homeassistant import config_entries
from homeassistant.const import CONF_API_KEY, CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.test_util.aiohttp import (
    AiohttpClientMocker,
)

from custom_components.storagehub.const import DOMAIN

HOST = "http://example.test"
API_KEY = "shub_test"


def _stub_ok(mock: AiohttpClientMocker, host: str = HOST) -> None:
    mock.get(
        f"{host}/api/ha/status",
        json={"name": "StorageHub", "version": "1.1.0", "api_version": "v1"},
    )
    mock.get(f"{host}/api/ha/stats", json={"total_items": 5})


async def test_user_flow_happy_path(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    _stub_ok(aioclient_mock)

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_HOST: HOST, CONF_API_KEY: API_KEY},
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "StorageHub"
    assert result["data"] == {CONF_HOST: HOST, CONF_API_KEY: API_KEY}


async def test_user_flow_strips_trailing_slash(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    _stub_ok(aioclient_mock)

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_HOST: f"{HOST}/", CONF_API_KEY: API_KEY},
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"][CONF_HOST] == HOST


async def test_user_flow_invalid_auth(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    aioclient_mock.get(
        f"{HOST}/api/ha/status",
        json={"name": "StorageHub", "version": "1.1.0", "api_version": "v1"},
    )
    aioclient_mock.get(f"{HOST}/api/ha/stats", status=401)

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_HOST: HOST, CONF_API_KEY: "bad"},
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "invalid_auth"}


async def test_user_flow_cannot_connect(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    import aiohttp

    aioclient_mock.get(
        f"{HOST}/api/ha/status",
        exc=aiohttp.ClientConnectionError("nope"),
    )

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_HOST: HOST, CONF_API_KEY: API_KEY},
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}


async def test_duplicate_host_aborts(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    MockConfigEntry(
        domain=DOMAIN,
        unique_id=HOST,
        data={CONF_HOST: HOST, CONF_API_KEY: API_KEY},
    ).add_to_hass(hass)

    _stub_ok(aioclient_mock)
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_HOST: HOST, CONF_API_KEY: API_KEY},
    )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"
