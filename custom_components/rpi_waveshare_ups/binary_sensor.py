"""Binary sensor entities."""

# region #-- imports --#
from dataclasses import dataclass
from typing import Callable

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from . import UPSData, UPSEntity
from .const import (
    CONF_COORDINATOR,
    CONF_HAT_TYPE,
    CONF_MIN_CHARGING,
    DEF_MIN_CHARGING,
    DOMAIN,
    HAT_TYPE_E,
)

# endregion


@dataclass
class UPSBinarySensorDescriptionMixin:
    """Additional attributes of the binary sensor description."""

    value_fn: Callable[[UPSData], bool | None]


@dataclass
class UPSBinarySensorEntityDescription(
    BinarySensorEntityDescription, UPSBinarySensorDescriptionMixin
):
    """Describes UPS binary sensor entity."""


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Create the binary sensor entities."""
    coordinator: DataUpdateCoordinator = hass.data[DOMAIN][CONF_COORDINATOR]
    descriptions = (
        HAT_E_BINARY_SENSOR_DESCRIPTIONS
        if config_entry.options.get(CONF_HAT_TYPE) == HAT_TYPE_E
        else (
            UPSBinarySensorEntityDescription(
                device_class=BinarySensorDeviceClass.BATTERY_CHARGING,
                key="battery_state",
                name="Battery State",
                translation_key="battery_state",
                value_fn=lambda u: u.current
                >= config_entry.options.get(CONF_MIN_CHARGING, DEF_MIN_CHARGING),
            ),
        )
    )

    binary_sensors: list[UPSBinarySensorEntity] = [
        UPSBinarySensorEntity(
            config_entry=config_entry,
            coordinator=coordinator,
            description=description,
        )
        for description in descriptions
    ]

    async_add_entities(binary_sensors, update_before_add=True)


class UPSBinarySensorEntity(UPSEntity, BinarySensorEntity):
    """Representation of a UPS binary sensor."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        description: UPSBinarySensorEntityDescription,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialise."""
        super().__init__(config_entry=config_entry, coordinator=coordinator)
        self.entity_description = description
        self._attr_has_entity_name = True
        self._attr_unique_id = (
            f"{config_entry.entry_id}::binary_sensor::{self.entity_description.key}"
        )

    @property
    def is_on(self) -> bool | None:
        """Return binary sensor state."""
        return self.entity_description.value_fn(self.coordinator.data)


HAT_E_BINARY_SENSOR_DESCRIPTIONS: tuple[UPSBinarySensorEntityDescription, ...] = (
    UPSBinarySensorEntityDescription(
        device_class=BinarySensorDeviceClass.BATTERY_CHARGING,
        key="charging",
        name="Charging",
        translation_key="charging",
        value_fn=lambda u: u.charging,
    ),
    UPSBinarySensorEntityDescription(
        key="fast_charging",
        name="Fast Charging",
        translation_key="fast_charging",
        value_fn=lambda u: u.fast_charging,
    ),
    UPSBinarySensorEntityDescription(
        device_class=BinarySensorDeviceClass.POWER,
        key="vbus_powered",
        name="VBUS Powered",
        translation_key="vbus_powered",
        value_fn=lambda u: u.vbus_powered,
    ),
    UPSBinarySensorEntityDescription(
        entity_registry_enabled_default=False,
        key="bq4050_communication",
        name="BQ4050 Communication",
        translation_key="bq4050_communication",
        value_fn=lambda u: u.bq4050_communication,
    ),
    UPSBinarySensorEntityDescription(
        entity_registry_enabled_default=False,
        key="ip2368_communication",
        name="IP2368 Communication",
        translation_key="ip2368_communication",
        value_fn=lambda u: u.ip2368_communication,
    ),
)
