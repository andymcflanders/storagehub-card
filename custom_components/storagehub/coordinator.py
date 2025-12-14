"""DataUpdateCoordinator for StorageHub."""

from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .api import CannotConnect, InvalidAuth, StorageHubApiClient
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class StorageHubData:
    """Class to hold StorageHub data."""

    def __init__(
        self,
        stats: dict[str, Any],
        reminders: dict[str, Any],
        connected: bool = True,
    ) -> None:
        """Initialize StorageHub data.

        Args:
            stats: Inventory statistics
            reminders: Reminder summary
            connected: Whether API is connected
        """
        self.stats = stats
        self.reminders = reminders
        self.connected = connected

    @property
    def total_items(self) -> int:
        """Return total item count."""
        return self.stats.get("total_items", 0)

    @property
    def total_containers(self) -> int:
        """Return total container count."""
        return self.stats.get("total_containers", 0)

    @property
    def total_locations(self) -> int:
        """Return total location count."""
        return self.stats.get("total_locations", 0)

    @property
    def overdue_reminders(self) -> int:
        """Return overdue reminder count."""
        return self.reminders.get("overdue_reminders", 0)

    @property
    def due_today(self) -> int:
        """Return reminders due today."""
        return self.reminders.get("due_today", 0)

    @property
    def due_this_week(self) -> int:
        """Return reminders due this week."""
        return self.reminders.get("due_this_week", 0)


class StorageHubDataUpdateCoordinator(DataUpdateCoordinator[StorageHubData]):
    """Class to manage fetching StorageHub data."""

    config_entry: ConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        api_client: StorageHubApiClient,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the coordinator.

        Args:
            hass: Home Assistant instance
            api_client: StorageHub API client
            config_entry: Config entry for this integration
        """
        self.api_client = api_client
        self.config_entry = config_entry

        # Get update interval from config or use default
        scan_interval = config_entry.options.get(
            CONF_SCAN_INTERVAL,
            config_entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
        )

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )

    async def _async_update_data(self) -> StorageHubData:
        """Fetch data from StorageHub API.

        Returns:
            StorageHubData containing stats and reminders

        Raises:
            UpdateFailed: If data cannot be fetched
        """
        try:
            stats = await self.api_client.async_get_stats()
            reminders = await self.api_client.async_get_reminders()

            return StorageHubData(
                stats=stats,
                reminders=reminders,
                connected=True,
            )

        except InvalidAuth as err:
            raise UpdateFailed(f"Authentication failed: {err}") from err
        except CannotConnect as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err
        except Exception as err:
            raise UpdateFailed(f"Unexpected error: {err}") from err
