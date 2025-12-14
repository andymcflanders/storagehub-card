"""Binary sensor platform for StorageHub."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import StorageHubData, StorageHubDataUpdateCoordinator


@dataclass(frozen=True, kw_only=True)
class StorageHubBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Describes StorageHub binary sensor entity."""

    is_on_fn: Callable[[StorageHubData | None, bool], bool]


BINARY_SENSOR_DESCRIPTIONS: tuple[StorageHubBinarySensorEntityDescription, ...] = (
    StorageHubBinarySensorEntityDescription(
        key="connected",
        translation_key="connected",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        is_on_fn=lambda data, last_success: last_success,
    ),
    StorageHubBinarySensorEntityDescription(
        key="has_overdue_reminders",
        translation_key="has_overdue_reminders",
        icon="mdi:bell-alert",
        device_class=BinarySensorDeviceClass.PROBLEM,
        is_on_fn=lambda data, _: data.overdue_reminders > 0 if data else False,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up StorageHub binary sensors based on a config entry."""
    coordinator: StorageHubDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id][
        "coordinator"
    ]

    async_add_entities(
        StorageHubBinarySensor(coordinator, description)
        for description in BINARY_SENSOR_DESCRIPTIONS
    )


class StorageHubBinarySensor(
    CoordinatorEntity[StorageHubDataUpdateCoordinator], BinarySensorEntity
):
    """Representation of a StorageHub binary sensor."""

    entity_description: StorageHubBinarySensorEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: StorageHubDataUpdateCoordinator,
        description: StorageHubBinarySensorEntityDescription,
    ) -> None:
        """Initialize the binary sensor.

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
    def is_on(self) -> bool:
        """Return true if the binary sensor is on."""
        # Check if last update was successful
        last_update_success = self.coordinator.last_update_success
        return self.entity_description.is_on_fn(
            self.coordinator.data, last_update_success
        )
