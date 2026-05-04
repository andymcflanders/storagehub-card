"""Sensor platform for StorageHub."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import CONF_HOST, EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import StorageHubConfigEntry
from .const import DOMAIN
from .coordinator import HeartbeatCoordinator, HeartbeatData, IndexCoordinator


@dataclass(frozen=True, kw_only=True)
class StorageHubSensorDescription(SensorEntityDescription):
    """Describe a StorageHub sensor."""

    value_fn: Callable[[HeartbeatData], int | str | None]


SENSORS: tuple[StorageHubSensorDescription, ...] = (
    StorageHubSensorDescription(
        key="total_items",
        translation_key="total_items",
        icon="mdi:package-variant",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="items",
        value_fn=lambda data: data.stats.total_items,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: StorageHubConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Register the heartbeat sensors for this config entry."""
    coordinator = entry.runtime_data.heartbeat
    async_add_entities(
        StorageHubSensor(coordinator, entry, description) for description in SENSORS
    )
    async_add_entities([StorageHubIndexEtagSensor(entry.runtime_data.index, entry)])


class StorageHubSensor(CoordinatorEntity[HeartbeatCoordinator], SensorEntity):
    """A single StorageHub sensor backed by the heartbeat coordinator."""

    _attr_has_entity_name = True
    entity_description: StorageHubSensorDescription

    def __init__(
        self,
        coordinator: HeartbeatCoordinator,
        entry: StorageHubConfigEntry,
        description: StorageHubSensorDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.unique_id}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            manufacturer="StorageHub",
            model="Inventory",
            configuration_url=entry.data[CONF_HOST],
            sw_version=(coordinator.data.status.version if coordinator.data else None),
        )

    @property
    def native_value(self) -> int | str | None:
        if self.coordinator.data is None:
            return None
        return self.entity_description.value_fn(self.coordinator.data)


class StorageHubIndexEtagSensor(CoordinatorEntity[IndexCoordinator], SensorEntity):
    """Diagnostic sensor exposing the cached index ETag.

    The Lovelace card subscribes to this entity's `state_changed` events
    so it knows to re-fetch `storagehub.search_lite` when the backend's
    index payload changes. Disabled by default — only users running the
    card need to enable it.
    """

    _attr_has_entity_name = True
    _attr_translation_key = "index_etag"
    _attr_icon = "mdi:database-sync"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_entity_registry_enabled_default = False

    def __init__(
        self, coordinator: IndexCoordinator, entry: StorageHubConfigEntry
    ) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.unique_id}_index_etag"
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, entry.entry_id)})

    @property
    def native_value(self) -> str | None:
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.etag
