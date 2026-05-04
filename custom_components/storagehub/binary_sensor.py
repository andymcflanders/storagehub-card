"""Binary sensor platform for StorageHub."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import StorageHubConfigEntry
from .const import DOMAIN
from .coordinator import HeartbeatCoordinator

CONNECTED_DESCRIPTION = BinarySensorEntityDescription(
    key="connected",
    translation_key="connected",
    device_class=BinarySensorDeviceClass.CONNECTIVITY,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: StorageHubConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Register the connectivity binary sensor."""
    async_add_entities([ConnectedBinarySensor(entry.runtime_data.heartbeat, entry)])


class ConnectedBinarySensor(
    CoordinatorEntity[HeartbeatCoordinator], BinarySensorEntity
):
    """Reflects whether the most recent heartbeat fetch succeeded."""

    _attr_has_entity_name = True
    entity_description = CONNECTED_DESCRIPTION

    def __init__(
        self,
        coordinator: HeartbeatCoordinator,
        entry: StorageHubConfigEntry,
    ) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.unique_id}_connected"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            manufacturer="StorageHub",
            model="Inventory",
            configuration_url=entry.data[CONF_HOST],
        )

    @property
    def is_on(self) -> bool:
        return self.coordinator.last_update_success

    @property
    def available(self) -> bool:
        # A connectivity sensor reports state even when the underlying
        # poll has failed, otherwise the off-state would be invisible.
        return True
