"""DataUpdateCoordinator for the StorageHub heartbeat."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .api import (
    CannotConnect,
    InvalidAuth,
    InventoryStats,
    StorageHubApiClient,
    StorageHubError,
    SystemStatus,
)
from .const import DOMAIN, HEARTBEAT_INTERVAL

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class HeartbeatData:
    """Bundle returned by the heartbeat coordinator."""

    status: SystemStatus
    stats: InventoryStats


class HeartbeatCoordinator(DataUpdateCoordinator[HeartbeatData]):
    """Polls /status + /stats so HA knows the integration is alive."""

    config_entry: ConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        client: StorageHubApiClient,
        config_entry: ConfigEntry,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            config_entry=config_entry,
            name=f"{DOMAIN}_heartbeat",
            update_interval=timedelta(seconds=HEARTBEAT_INTERVAL),
        )
        self._client = client

    async def _async_update_data(self) -> HeartbeatData:
        try:
            status = await self._client.async_get_status()
            stats = await self._client.async_get_stats()
        except InvalidAuth as err:
            raise ConfigEntryAuthFailed(str(err)) from err
        except (CannotConnect, StorageHubError) as err:
            raise UpdateFailed(str(err)) from err
        return HeartbeatData(status=status, stats=stats)
