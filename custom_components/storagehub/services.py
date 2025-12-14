"""Services for StorageHub integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant.core import (
    HomeAssistant,
    ServiceCall,
    ServiceResponse,
    SupportsResponse,
)
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from homeassistant.helpers import config_validation as cv

from .api import CannotConnect, InvalidAuth, StorageHubApiError
from .const import (
    DOMAIN,
    SERVICE_GET_CONTAINER,
    SERVICE_REFRESH,
    SERVICE_SEARCH,
)

_LOGGER = logging.getLogger(__name__)

SEARCH_SCHEMA = vol.Schema(
    {
        vol.Required("query"): cv.string,
        vol.Optional("limit", default=10): vol.All(
            vol.Coerce(int), vol.Range(min=1, max=50)
        ),
    }
)

GET_CONTAINER_SCHEMA = vol.Schema(
    {
        vol.Required("qr_code"): cv.string,
    }
)


def _get_api_client(hass: HomeAssistant) -> Any:
    """Get the API client from the first config entry.

    Args:
        hass: Home Assistant instance

    Returns:
        StorageHubApiClient instance

    Raises:
        ServiceValidationError: If no StorageHub integration is configured
    """
    if DOMAIN not in hass.data or not hass.data[DOMAIN]:
        raise ServiceValidationError(
            translation_domain=DOMAIN,
            translation_key="no_config_entry",
        )

    # Get the first (or only) config entry's API client
    entry_data = next(iter(hass.data[DOMAIN].values()))
    return entry_data["api_client"]


async def async_setup_services(hass: HomeAssistant) -> None:
    """Set up StorageHub services."""

    async def handle_search(call: ServiceCall) -> ServiceResponse:
        """Handle the search service call.

        Args:
            call: Service call data

        Returns:
            Search results with items, total_count, and query
        """
        api_client = _get_api_client(hass)

        try:
            result = await api_client.async_search(
                query=call.data["query"],
                limit=call.data.get("limit", 10),
            )

            return {
                "items": result.get("items", []),
                "total_count": result.get("total_count", 0),
                "query": result.get("query", call.data["query"]),
            }

        except InvalidAuth as err:
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key="auth_failed",
            ) from err
        except CannotConnect as err:
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key="cannot_connect",
            ) from err
        except StorageHubApiError as err:
            raise HomeAssistantError(f"StorageHub API error: {err}") from err

    async def handle_get_container(call: ServiceCall) -> ServiceResponse:
        """Handle the get_container service call.

        Args:
            call: Service call data

        Returns:
            Container details including items
        """
        api_client = _get_api_client(hass)

        try:
            result = await api_client.async_get_container_by_qr(
                qr_code=call.data["qr_code"],
            )
            return result

        except InvalidAuth as err:
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key="auth_failed",
            ) from err
        except CannotConnect as err:
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key="cannot_connect",
            ) from err
        except StorageHubApiError as err:
            # Check if it's a 404 (container not found)
            if "404" in str(err):
                raise ServiceValidationError(
                    translation_domain=DOMAIN,
                    translation_key="container_not_found",
                    translation_placeholders={"qr_code": call.data["qr_code"]},
                ) from err
            raise HomeAssistantError(f"StorageHub API error: {err}") from err

    async def handle_refresh(call: ServiceCall) -> None:
        """Handle the refresh service call.

        Args:
            call: Service call data (unused)
        """
        for entry_data in hass.data[DOMAIN].values():
            coordinator = entry_data["coordinator"]
            await coordinator.async_request_refresh()

    # Register services
    hass.services.async_register(
        DOMAIN,
        SERVICE_SEARCH,
        handle_search,
        schema=SEARCH_SCHEMA,
        supports_response=SupportsResponse.ONLY,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_GET_CONTAINER,
        handle_get_container,
        schema=GET_CONTAINER_SCHEMA,
        supports_response=SupportsResponse.ONLY,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_REFRESH,
        handle_refresh,
    )


async def async_unload_services(hass: HomeAssistant) -> None:
    """Unload StorageHub services."""
    hass.services.async_remove(DOMAIN, SERVICE_SEARCH)
    hass.services.async_remove(DOMAIN, SERVICE_GET_CONTAINER)
    hass.services.async_remove(DOMAIN, SERVICE_REFRESH)
