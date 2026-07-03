"""Sensor entities."""

# region #-- imports --#
from dataclasses import dataclass
from typing import Callable

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfPower,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from . import UPSData, UPSEntity
from .const import CONF_COORDINATOR, CONF_HAT_TYPE, DOMAIN, HAT_TYPE_E

# endregion


@dataclass
class UPSSensorEntityDescription(SensorEntityDescription):
    """Describes UPS sensor entity."""

    value_fn: Callable[[UPSData], StateType] | None = None


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Create the sensor entities."""
    coordinator: DataUpdateCoordinator = hass.data[DOMAIN][CONF_COORDINATOR]
    descriptions = (
        HAT_E_SENSOR_DESCRIPTIONS
        if config_entry.options.get(CONF_HAT_TYPE) == HAT_TYPE_E
        else SENSOR_DESCRIPTIONS
    )

    sensors: list[UPSSensorEntity] = [
        UPSSensorEntity(
            config_entry=config_entry,
            coordinator=coordinator,
            description=description,
        )
        for description in descriptions
    ]

    async_add_entities(sensors, update_before_add=True)


class UPSSensorEntity(UPSEntity, SensorEntity):
    """Representation of a UPS sensor."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        description: UPSSensorEntityDescription,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialise."""
        super().__init__(config_entry=config_entry, coordinator=coordinator)
        self.entity_description = description
        self._attr_has_entity_name = True
        self._attr_unique_id = (
            f"{config_entry.entry_id}::sensor::{self.entity_description.key}"
        )

    @property
    def native_value(self) -> StateType:
        """Return the value reported by the sensor."""
        if self.entity_description.value_fn is not None:
            return self.entity_description.value_fn(self.coordinator.data)

        return getattr(self.coordinator.data, self.entity_description.key, None)


SENSOR_DESCRIPTIONS: tuple[UPSSensorEntityDescription, ...] = (
    UPSSensorEntityDescription(
        device_class=SensorDeviceClass.BATTERY,
        key="battery_percentage",
        name="Battery Level",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        translation_key="battery_percentage",
    ),
    UPSSensorEntityDescription(
        device_class=SensorDeviceClass.CURRENT,
        key="current",
        name="Current",
        native_unit_of_measurement=UnitOfElectricCurrent.MILLIAMPERE,
        state_class=SensorStateClass.MEASUREMENT,
        translation_key="current",
    ),
    UPSSensorEntityDescription(
        device_class=SensorDeviceClass.VOLTAGE,
        key="load_voltage",
        name="Load Voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
        translation_key="load_voltage",
    ),
    UPSSensorEntityDescription(
        device_class=SensorDeviceClass.POWER,
        key="power",
        name="Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        translation_key="power",
    ),
    UPSSensorEntityDescription(
        device_class=SensorDeviceClass.VOLTAGE,
        key="psu_voltage",
        name="PSU Voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
        translation_key="psu_voltage",
        value_fn=lambda u: u.load_voltage + u.shunt_voltage,
    ),
    UPSSensorEntityDescription(
        device_class=SensorDeviceClass.VOLTAGE,
        key="shunt_voltage",
        name="Shunt Voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
        translation_key="shunt_voltage",
    ),
)

HAT_E_SENSOR_DESCRIPTIONS: tuple[UPSSensorEntityDescription, ...] = (
    UPSSensorEntityDescription(
        key="charge_state",
        name="Charge State",
        translation_key="charge_state",
    ),
    UPSSensorEntityDescription(
        device_class=SensorDeviceClass.VOLTAGE,
        key="vbus_voltage",
        name="VBUS Voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
        translation_key="vbus_voltage",
    ),
    UPSSensorEntityDescription(
        device_class=SensorDeviceClass.CURRENT,
        key="vbus_current",
        name="VBUS Current",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        state_class=SensorStateClass.MEASUREMENT,
        translation_key="vbus_current",
    ),
    UPSSensorEntityDescription(
        device_class=SensorDeviceClass.POWER,
        key="vbus_power",
        name="VBUS Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        translation_key="vbus_power",
    ),
    UPSSensorEntityDescription(
        device_class=SensorDeviceClass.VOLTAGE,
        key="battery_voltage",
        name="Battery Voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
        translation_key="battery_voltage",
    ),
    UPSSensorEntityDescription(
        device_class=SensorDeviceClass.CURRENT,
        key="battery_current",
        name="Battery Current",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        state_class=SensorStateClass.MEASUREMENT,
        translation_key="battery_current",
    ),
    UPSSensorEntityDescription(
        device_class=SensorDeviceClass.BATTERY,
        key="battery_percentage",
        name="Battery Level",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        translation_key="battery_percentage",
    ),
    UPSSensorEntityDescription(
        key="remaining_capacity",
        name="Remaining Capacity",
        native_unit_of_measurement="mAh",
        state_class=SensorStateClass.MEASUREMENT,
        translation_key="remaining_capacity",
    ),
    UPSSensorEntityDescription(
        key="runtime_to_empty",
        name="Runtime To Empty",
        native_unit_of_measurement=UnitOfTime.MINUTES,
        state_class=SensorStateClass.MEASUREMENT,
        translation_key="runtime_to_empty",
    ),
    UPSSensorEntityDescription(
        key="time_to_full",
        name="Time To Full",
        native_unit_of_measurement=UnitOfTime.MINUTES,
        state_class=SensorStateClass.MEASUREMENT,
        translation_key="time_to_full",
    ),
    UPSSensorEntityDescription(
        device_class=SensorDeviceClass.VOLTAGE,
        key="cell_1_voltage",
        name="Cell 1 Voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
        translation_key="cell_1_voltage",
    ),
    UPSSensorEntityDescription(
        device_class=SensorDeviceClass.VOLTAGE,
        key="cell_2_voltage",
        name="Cell 2 Voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
        translation_key="cell_2_voltage",
    ),
    UPSSensorEntityDescription(
        device_class=SensorDeviceClass.VOLTAGE,
        key="cell_3_voltage",
        name="Cell 3 Voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
        translation_key="cell_3_voltage",
    ),
    UPSSensorEntityDescription(
        device_class=SensorDeviceClass.VOLTAGE,
        key="cell_4_voltage",
        name="Cell 4 Voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
        translation_key="cell_4_voltage",
    ),
    UPSSensorEntityDescription(
        entity_registry_enabled_default=False,
        key="device_id",
        name="Device ID",
        translation_key="device_id",
    ),
    UPSSensorEntityDescription(
        entity_registry_enabled_default=False,
        key="control_register",
        name="Control Register",
        translation_key="control_register",
    ),
    UPSSensorEntityDescription(
        entity_registry_enabled_default=False,
        key="configured_i2c_address",
        name="Configured I2C Address",
        translation_key="configured_i2c_address",
    ),
    UPSSensorEntityDescription(
        entity_registry_enabled_default=False,
        key="watchdog_timeout",
        name="Watchdog Timeout",
        native_unit_of_measurement=UnitOfTime.SECONDS,
        translation_key="watchdog_timeout",
    ),
    UPSSensorEntityDescription(
        entity_registry_enabled_default=False,
        key="watchdog_startup_delay",
        name="Watchdog Startup Delay",
        native_unit_of_measurement=UnitOfTime.SECONDS,
        translation_key="watchdog_startup_delay",
    ),
    UPSSensorEntityDescription(
        entity_registry_enabled_default=False,
        key="software_revision",
        name="Software Revision",
        translation_key="software_revision",
    ),
)
