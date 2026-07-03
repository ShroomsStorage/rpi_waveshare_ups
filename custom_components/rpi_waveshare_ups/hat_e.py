"""Reader for Waveshare UPS HAT (E)."""

# region #-- imports --#
from dataclasses import dataclass
from enum import IntEnum
from typing import Any

# endregion


class HatERegister(IntEnum):
    """Register addresses for UPS HAT (E)."""

    DEVICE_ID = 0x00
    STATUS = 0x02
    COMMUNICATION_STATUS = 0x03
    VBUS = 0x10
    BATTERY = 0x20
    CELLS = 0x30
    CONTROL = 0x40
    I2C_ADDRESS = 0x41
    WATCHDOG_TIMEOUT = 0x42
    WATCHDOG_STARTUP_DELAY = 0x43
    SOFTWARE_REVISION = 0x50


STATUS_CHARGING = 0x80
STATUS_FAST_CHARGING = 0x40
STATUS_VBUS_POWERED = 0x20
STATUS_CHARGE_STATE = 0x07

COMMUNICATION_BQ4050 = 0x02
COMMUNICATION_IP2368 = 0x01

CHARGE_STATES: dict[int, str] = {
    0: "standby",
    1: "trickle",
    2: "constant_current",
    3: "constant_voltage",
    4: "pending",
    5: "full",
    6: "timeout",
}


class HatEUpdateError(Exception):
    """Raised when UPS HAT (E) data cannot be read."""


@dataclass
class HatEData:
    """UPS HAT (E) data snapshot."""

    charging: bool
    fast_charging: bool
    vbus_powered: bool
    charge_state: str
    vbus_voltage: float
    vbus_current: float
    vbus_power: float
    battery_voltage: float
    battery_current: float
    battery_percentage: int
    remaining_capacity: int
    runtime_to_empty: int
    time_to_full: int
    cell_1_voltage: float
    cell_2_voltage: float
    cell_3_voltage: float
    cell_4_voltage: float
    device_id: int | None = None
    bq4050_communication: bool | None = None
    ip2368_communication: bool | None = None
    control_register: int | None = None
    configured_i2c_address: int | None = None
    watchdog_timeout: int | None = None
    watchdog_startup_delay: int | None = None
    software_revision: str | None = None


def u16_le(data: list[int], offset: int = 0) -> int:
    """Convert two little-endian bytes from data to an unsigned integer."""
    return data[offset] | data[offset + 1] << 8


def i16_le(data: list[int], offset: int = 0) -> int:
    """Convert two little-endian bytes from data to a signed integer."""
    value = u16_le(data, offset)
    if value >= 0x8000:
        value -= 0x10000
    return value


def software_revision(value: int | None) -> str | None:
    """Convert the HAT E software revision register to a display value."""
    if value is None:
        return None
    return f"V{value >> 4}.{value & 0x0F}"


def parse_hat_e_data(
    status: int,
    vbus: list[int],
    battery: list[int],
    cells: list[int],
    device_id: int | None = None,
    communication_status: int | None = None,
    control_register: int | None = None,
    configured_i2c_address: int | None = None,
    watchdog_timeout: int | None = None,
    watchdog_startup_delay: int | None = None,
    software_revision_value: int | None = None,
) -> HatEData:
    """Parse UPS HAT (E) register bytes into scaled data."""
    return HatEData(
        charging=bool(status & STATUS_CHARGING),
        fast_charging=bool(status & STATUS_FAST_CHARGING),
        vbus_powered=bool(status & STATUS_VBUS_POWERED),
        charge_state=CHARGE_STATES.get(status & STATUS_CHARGE_STATE, "unknown"),
        vbus_voltage=u16_le(vbus) / 1000,
        vbus_current=u16_le(vbus, 2) / 1000,
        vbus_power=u16_le(vbus, 4) / 1000,
        battery_voltage=u16_le(battery) / 1000,
        battery_current=i16_le(battery, 2) / 1000,
        battery_percentage=u16_le(battery, 4),
        remaining_capacity=u16_le(battery, 6),
        runtime_to_empty=u16_le(battery, 8),
        time_to_full=u16_le(battery, 10),
        cell_1_voltage=u16_le(cells) / 1000,
        cell_2_voltage=u16_le(cells, 2) / 1000,
        cell_3_voltage=u16_le(cells, 4) / 1000,
        cell_4_voltage=u16_le(cells, 6) / 1000,
        device_id=device_id,
        bq4050_communication=None
        if communication_status is None
        else bool(communication_status & COMMUNICATION_BQ4050),
        ip2368_communication=None
        if communication_status is None
        else bool(communication_status & COMMUNICATION_IP2368),
        control_register=control_register,
        configured_i2c_address=configured_i2c_address,
        watchdog_timeout=watchdog_timeout,
        watchdog_startup_delay=watchdog_startup_delay,
        software_revision=software_revision(software_revision_value),
    )


class HatE:
    """Read UPS HAT (E) data over I2C."""

    def __init__(self, addr: int, i2c_bus: int) -> None:
        """Initialise."""
        import smbus2 as smbus

        self.bus: Any = smbus.SMBus(i2c_bus)
        self.addr: int = addr

    def read_u8(self, register: int) -> int:
        """Read an unsigned 8-bit value."""
        return self.bus.read_i2c_block_data(self.addr, register, 1)[0]

    def read_u16_le(self, register: int) -> int:
        """Read an unsigned little-endian 16-bit value."""
        return u16_le(self.bus.read_i2c_block_data(self.addr, register, 2))

    def read_i16_le(self, register: int) -> int:
        """Read a signed little-endian 16-bit value."""
        return i16_le(self.bus.read_i2c_block_data(self.addr, register, 2))

    def _optional_u8(self, register: int) -> int | None:
        """Read an optional diagnostic register without failing the update."""
        try:
            return self.read_u8(register)
        except OSError:
            return None

    def read_data(self) -> HatEData:
        """Read and parse all UPS HAT (E) data."""
        try:
            status = self.read_u8(HatERegister.STATUS)
            vbus = self.bus.read_i2c_block_data(self.addr, HatERegister.VBUS, 6)
            battery = self.bus.read_i2c_block_data(self.addr, HatERegister.BATTERY, 12)
            cells = self.bus.read_i2c_block_data(self.addr, HatERegister.CELLS, 8)
        except OSError as err:
            raise HatEUpdateError("Unable to read UPS HAT (E) registers") from err

        return parse_hat_e_data(
            status=status,
            vbus=vbus,
            battery=battery,
            cells=cells,
            device_id=self._optional_u8(HatERegister.DEVICE_ID),
            communication_status=self._optional_u8(HatERegister.COMMUNICATION_STATUS),
            control_register=self._optional_u8(HatERegister.CONTROL),
            configured_i2c_address=self._optional_u8(HatERegister.I2C_ADDRESS),
            watchdog_timeout=self._optional_u8(HatERegister.WATCHDOG_TIMEOUT),
            watchdog_startup_delay=self._optional_u8(
                HatERegister.WATCHDOG_STARTUP_DELAY
            ),
            software_revision_value=self._optional_u8(HatERegister.SOFTWARE_REVISION),
        )
