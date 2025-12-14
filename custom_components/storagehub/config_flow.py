"""Config flow for StorageHub integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_SCAN_INTERVAL
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import CannotConnect, InvalidAuth, StorageHubApiClient
from .const import (
    CONF_API_KEY,
    CONF_HOST,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST, default="http://storagehub.local"): str,
        vol.Required(CONF_API_KEY): str,
        vol.Optional(
            CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL
        ): vol.All(vol.Coerce(int), vol.Range(min=60, max=3600)),
    }
)


class StorageHubConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for StorageHub."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                # Normalize host URL
                host = user_input[CONF_HOST].rstrip("/")
                user_input[CONF_HOST] = host

                # Create API client and test connection
                session = async_get_clientsession(self.hass)
                client = StorageHubApiClient(
                    session=session,
                    host=host,
                    api_key=user_input[CONF_API_KEY],
                )

                # Test connection and get status
                status = await client.async_get_status()
                await client.async_get_stats()  # Verify auth works

                # Set unique ID based on host
                await self.async_set_unique_id(host)
                self._abort_if_unique_id_configured()

                # Create entry
                title = status.get("name", "StorageHub")
                return self.async_create_entry(title=title, data=user_input)

            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # noqa: BLE001
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    @staticmethod
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> StorageHubOptionsFlow:
        """Get the options flow for this handler."""
        return StorageHubOptionsFlow(config_entry)


class StorageHubOptionsFlow(config_entries.OptionsFlow):
    """Handle StorageHub options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_SCAN_INTERVAL,
                        default=self.config_entry.options.get(
                            CONF_SCAN_INTERVAL,
                            self.config_entry.data.get(
                                CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                            ),
                        ),
                    ): vol.All(vol.Coerce(int), vol.Range(min=60, max=3600)),
                }
            ),
        )
