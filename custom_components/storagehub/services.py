"""Service registration for StorageHub."""

from __future__ import annotations

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

from . import StorageHubData
from .api import CannotConnect, InvalidAuth, SearchResultItem, StorageHubError
from .const import DOMAIN

SERVICE_SEARCH = "search"

_SEARCH_SCHEMA = vol.Schema(
    {
        vol.Required("query"): vol.All(cv.string, vol.Length(min=2)),
        vol.Optional("limit", default=20): vol.All(
            vol.Coerce(int), vol.Range(min=1, max=50)
        ),
    }
)


async def async_register_services(hass: HomeAssistant) -> None:
    """Register StorageHub services exactly once per HA process."""
    if hass.services.has_service(DOMAIN, SERVICE_SEARCH):
        return

    async def _handle_search(call: ServiceCall) -> ServiceResponse:
        entries = hass.config_entries.async_loaded_entries(DOMAIN)
        if not entries:
            raise ServiceValidationError(
                translation_domain=DOMAIN, translation_key="not_configured"
            )

        data: StorageHubData = entries[0].runtime_data
        query = call.data["query"]
        limit = call.data["limit"]

        try:
            result = await data.client.async_search(query, limit=limit)
        except InvalidAuth as err:
            raise HomeAssistantError(
                translation_domain=DOMAIN, translation_key="auth_failed"
            ) from err
        except CannotConnect as err:
            raise HomeAssistantError(
                translation_domain=DOMAIN, translation_key="cannot_connect"
            ) from err
        except StorageHubError as err:
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key="api_error",
                translation_placeholders={"detail": str(err)},
            ) from err

        return {
            "items": [_serialize_item(item) for item in result.items],
            "total_count": result.total_count,
            "query": result.query,
        }

    hass.services.async_register(
        DOMAIN,
        SERVICE_SEARCH,
        _handle_search,
        schema=_SEARCH_SCHEMA,
        supports_response=SupportsResponse.ONLY,
    )


def _serialize_item(item: SearchResultItem) -> dict[str, Any]:
    return {
        "id": item.id,
        "name": item.name,
        "description": item.description,
        "container_name": item.container_name,
        "location_name": item.location_name,
        "condition": item.condition,
        "seasonal": item.seasonal,
        "value_estimate": item.value_estimate,
        "owner_name": item.owner_name,
        "primary_image_url": item.primary_image_url,
        "tags": list(item.tags),
    }
