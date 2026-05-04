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
from .api import (
    CannotConnect,
    IndexEntry,
    InvalidAuth,
    SearchResultItem,
    StorageHubError,
)
from .const import DOMAIN

SERVICE_SEARCH = "search"
SERVICE_SEARCH_LITE = "search_lite"
SERVICE_REFRESH_INDEX = "refresh_index"

_SEARCH_SCHEMA = vol.Schema(
    {
        vol.Required("query"): vol.All(cv.string, vol.Length(min=2)),
        vol.Optional("limit", default=20): vol.All(
            vol.Coerce(int), vol.Range(min=1, max=50)
        ),
    }
)
_NO_FIELDS_SCHEMA = vol.Schema({})


async def async_register_services(hass: HomeAssistant) -> None:
    """Register StorageHub services exactly once per HA process."""
    if hass.services.has_service(DOMAIN, SERVICE_SEARCH):
        return

    async def _handle_search(call: ServiceCall) -> ServiceResponse:
        data = _resolve_runtime_data(hass)
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

    async def _handle_search_lite(call: ServiceCall) -> ServiceResponse:
        data = _resolve_runtime_data(hass)
        snapshot = data.index.data
        if snapshot is None:
            return {"etag": None, "items": [], "count": 0}
        return {
            "etag": snapshot.etag,
            "items": [_serialize_index_entry(entry) for entry in snapshot.entries],
            "count": len(snapshot.entries),
        }

    hass.services.async_register(
        DOMAIN,
        SERVICE_SEARCH_LITE,
        _handle_search_lite,
        schema=_NO_FIELDS_SCHEMA,
        supports_response=SupportsResponse.ONLY,
    )

    async def _handle_refresh_index(call: ServiceCall) -> None:
        data = _resolve_runtime_data(hass)
        await data.index.async_request_refresh()

    hass.services.async_register(
        DOMAIN,
        SERVICE_REFRESH_INDEX,
        _handle_refresh_index,
        schema=_NO_FIELDS_SCHEMA,
        supports_response=SupportsResponse.NONE,
    )


def _resolve_runtime_data(hass: HomeAssistant) -> StorageHubData:
    entries = hass.config_entries.async_loaded_entries(DOMAIN)
    if not entries:
        raise ServiceValidationError(
            translation_domain=DOMAIN, translation_key="not_configured"
        )
    return entries[0].runtime_data


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


def _serialize_index_entry(entry: IndexEntry) -> dict[str, Any]:
    return {
        "id": entry.id,
        "name": entry.name,
        "owner_name": entry.owner_name,
        "container_name": entry.container_name,
        "location_name": entry.location_name,
        "ai_names": list(entry.ai_names),
    }
