"""Config flow for StorageHub: user, reauth, reconfigure."""

from __future__ import annotations

from collections.abc import Mapping
import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_API_KEY, CONF_HOST
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import (
    CannotConnect,
    InvalidAuth,
    StorageHubApiClient,
    StorageHubError,
    SystemStatus,
)
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

_USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST, default="http://storagehub.local"): str,
        vol.Required(CONF_API_KEY): str,
    }
)


class StorageHubConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle the user-facing config flow."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Initial step where the user provides host + API key."""
        errors: dict[str, str] = {}
        if user_input is not None:
            host = user_input[CONF_HOST].rstrip("/")
            api_key = user_input[CONF_API_KEY]
            try:
                status = await self._validate(host, api_key)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except StorageHubError:
                _LOGGER.exception("Unexpected error while validating StorageHub")
                errors["base"] = "unknown"
            else:
                # instance_id is preferred (backend issue 3); host is the
                # fallback while older builds don't return one.
                await self.async_set_unique_id(status.instance_id or host)
                self._abort_if_unique_id_configured(
                    updates={CONF_HOST: host, CONF_API_KEY: api_key}
                )
                return self.async_create_entry(
                    title=status.name,
                    data={CONF_HOST: host, CONF_API_KEY: api_key},
                )
        return self.async_show_form(
            step_id="user", data_schema=_USER_SCHEMA, errors=errors
        )

    async def async_step_reauth(
        self, entry_data: Mapping[str, Any]
    ) -> ConfigFlowResult:
        """Triggered when the API key is rejected at runtime."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        entry = self._get_reauth_entry()
        if user_input is not None:
            host = entry.data[CONF_HOST]
            api_key = user_input[CONF_API_KEY]
            try:
                await self._validate(host, api_key)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except StorageHubError:
                errors["base"] = "unknown"
            else:
                return self.async_update_reload_and_abort(
                    entry, data={**entry.data, CONF_API_KEY: api_key}
                )
        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema({vol.Required(CONF_API_KEY): str}),
            errors=errors,
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Update the host/API key on an existing entry."""
        errors: dict[str, str] = {}
        entry = self._get_reconfigure_entry()
        if user_input is not None:
            host = user_input[CONF_HOST].rstrip("/")
            api_key = user_input[CONF_API_KEY]
            try:
                status = await self._validate(host, api_key)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except StorageHubError:
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(status.instance_id or host)
                # If instance_id is present, this guards against pointing the
                # entry at a *different* StorageHub. Pre-issue-3 backends
                # fall back to host comparison, which has the same effect.
                self._abort_if_unique_id_mismatch(reason="instance_mismatch")
                return self.async_update_reload_and_abort(
                    entry,
                    data={CONF_HOST: host, CONF_API_KEY: api_key},
                )
        return self.async_show_form(
            step_id="reconfigure",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST, default=entry.data[CONF_HOST]): str,
                    vol.Required(CONF_API_KEY): str,
                }
            ),
            errors=errors,
        )

    async def _validate(self, host: str, api_key: str) -> SystemStatus:
        """Confirm reachability and that the API key has read access."""
        session = async_get_clientsession(self.hass)
        client = StorageHubApiClient(session=session, host=host, api_key=api_key)
        status = await client.async_get_status()
        await client.async_get_stats()
        return status
