"""Sensor platform for StorageHub."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTR_DUE_THIS_WEEK,
    ATTR_DUE_TODAY,
    ATTR_ITEMS_BY_CONDITION,
    ATTR_ITEMS_BY_SEASON,
    ATTR_ITEMS_NEEDING_REVIEW,
    ATTR_PENDING_REMINDERS,
    ATTR_REMINDERS_BY_TYPE,
    ATTR_TOTAL_CONTAINERS,
    ATTR_TOTAL_LOCATIONS,
    ATTR_TOTAL_PHOTOS,
    ATTR_TOTAL_REMINDERS,
    ATTR_TOTAL_TAGS,
    DOMAIN,
)
from .coordinator import StorageHubData, StorageHubDataUpdateCoordinator


@dataclass(frozen=True, kw_only=True)
class StorageHubSensorEntityDescription(SensorEntityDescription):
    """Describes StorageHub sensor entity."""

    value_fn: Callable[[StorageHubData], int | str | None]
    extra_attrs_fn: Callable[[StorageHubData], dict[str, Any]] | None = None


SENSOR_DESCRIPTIONS: tuple[StorageHubSensorEntityDescription, ...] = (
    StorageHubSensorEntityDescription(
        key="total_items",
        translation_key="total_items",
        icon="mdi:package-variant",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="items",
        value_fn=lambda data: data.total_items,
        extra_attrs_fn=lambda data: {
            ATTR_TOTAL_LOCATIONS: data.total_locations,
            ATTR_TOTAL_CONTAINERS: data.total_containers,
            ATTR_TOTAL_PHOTOS: data.stats.get("total_photos", 0),
            ATTR_TOTAL_TAGS: data.stats.get("total_tags", 0),
            ATTR_ITEMS_NEEDING_REVIEW: data.stats.get("items_needing_review", 0),
            ATTR_ITEMS_BY_CONDITION: data.stats.get("items_by_condition", {}),
            ATTR_ITEMS_BY_SEASON: data.stats.get("items_by_season", {}),
        },
    ),
    StorageHubSensorEntityDescription(
        key="overdue_reminders",
        translation_key="overdue_reminders",
        icon="mdi:bell-alert",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="reminders",
        value_fn=lambda data: data.overdue_reminders,
        extra_attrs_fn=lambda data: {
            ATTR_TOTAL_REMINDERS: data.reminders.get("total_reminders", 0),
            ATTR_PENDING_REMINDERS: data.reminders.get("pending_reminders", 0),
            ATTR_DUE_TODAY: data.due_today,
            ATTR_DUE_THIS_WEEK: data.due_this_week,
            ATTR_REMINDERS_BY_TYPE: data.reminders.get("reminders_by_type", {}),
        },
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up StorageHub sensors based on a config entry."""
    coordinator: StorageHubDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id][
        "coordinator"
    ]

    async_add_entities(
        StorageHubSensor(coordinator, description)
        for description in SENSOR_DESCRIPTIONS
    )


class StorageHubSensor(
    CoordinatorEntity[StorageHubDataUpdateCoordinator], SensorEntity
):
    """Representation of a StorageHub sensor."""

    entity_description: StorageHubSensorEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: StorageHubDataUpdateCoordinator,
        description: StorageHubSensorEntityDescription,
    ) -> None:
        """Initialize the sensor.

        Args:
            coordinator: Data update coordinator
            description: Entity description
        """
        super().__init__(coordinator)
        self.entity_description = description

        # Set unique ID
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{description.key}"

        # Set device info
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.config_entry.entry_id)},
            "name": coordinator.config_entry.title,
            "manufacturer": "StorageHub",
            "model": "Inventory System",
            "configuration_url": coordinator.api_client.host,
        }

    @property
    def native_value(self) -> int | str | None:
        """Return the state of the sensor."""
        if self.coordinator.data is None:
            return None
        return self.entity_description.value_fn(self.coordinator.data)

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return extra state attributes."""
        if (
            self.coordinator.data is None
            or self.entity_description.extra_attrs_fn is None
        ):
            return None
        return self.entity_description.extra_attrs_fn(self.coordinator.data)
