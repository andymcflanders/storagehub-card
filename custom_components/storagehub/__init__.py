"""StorageHub Home Assistant integration."""

from __future__ import annotations

from dataclasses import dataclass
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY, CONF_HOST, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.typing import ConfigType

from .api import StorageHubApiClient
from .coordinator import HeartbeatCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.BINARY_SENSOR, Platform.SENSOR]


@dataclass(slots=True)
class StorageHubData:
    """Runtime container attached to the config entry."""

    client: StorageHubApiClient
    heartbeat: HeartbeatCoordinator


type StorageHubConfigEntry = ConfigEntry[StorageHubData]


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Register domain-level services once per HA process."""
    from .services import async_register_services

    await async_register_services(hass)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: StorageHubConfigEntry) -> bool:
    """Set up StorageHub from a config entry."""
    session = async_get_clientsession(hass)
    client = StorageHubApiClient(
        session=session,
        host=entry.data[CONF_HOST],
        api_key=entry.data[CONF_API_KEY],
    )
    heartbeat = HeartbeatCoordinator(hass, client, entry)
    await heartbeat.async_config_entry_first_refresh()

    entry.runtime_data = StorageHubData(client=client, heartbeat=heartbeat)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: StorageHubConfigEntry) -> bool:
    """Tear down a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
