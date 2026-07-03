"""Tests for UPS HAT (E) parsing."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys

MODULE_PATH = (
    Path(__file__).parents[1]
    / "custom_components"
    / "rpi_waveshare_ups"
    / "hat_e.py"
)
SPEC = spec_from_file_location("hat_e", MODULE_PATH)
hat_e = module_from_spec(SPEC)
sys.modules["hat_e"] = hat_e
SPEC.loader.exec_module(hat_e)


def test_i16_le_converts_twos_complement_values() -> None:
    """Test signed little-endian conversion."""
    assert hat_e.i16_le([0x01, 0x00]) == 1
    assert hat_e.i16_le([0xFF, 0x7F]) == 32767
    assert hat_e.i16_le([0x00, 0x80]) == -32768
    assert hat_e.i16_le([0xFF, 0xFF]) == -1


def test_parse_hat_e_data_scales_register_values() -> None:
    """Test HAT E register parsing and scaling."""
    data = hat_e.parse_hat_e_data(
        status=0xE3,
        vbus=[0x88, 0x13, 0xF4, 0x01, 0x10, 0x27],
        battery=[
            0x34,
            0x12,
            0xFF,
            0xFF,
            0x64,
            0x00,
            0xD0,
            0x07,
            0x3C,
            0x00,
            0x78,
            0x00,
        ],
        cells=[0xB8, 0x0B, 0xBA, 0x0B, 0xBC, 0x0B, 0xBE, 0x0B],
        device_id=0x0A,
        communication_status=0x03,
        control_register=0x55,
        configured_i2c_address=0x2D,
        watchdog_timeout=10,
        watchdog_startup_delay=20,
        software_revision_value=0x14,
    )

    assert data.charging is True
    assert data.fast_charging is True
    assert data.vbus_powered is True
    assert data.charge_state == "constant_voltage"
    assert data.vbus_voltage == 5.0
    assert data.vbus_current == 0.5
    assert data.vbus_power == 10.0
    assert data.battery_voltage == 4.66
    assert data.battery_current == -0.001
    assert data.battery_percentage == 100
    assert data.remaining_capacity == 2000
    assert data.runtime_to_empty == 60
    assert data.time_to_full == 120
    assert data.cell_1_voltage == 3.0
    assert data.cell_2_voltage == 3.002
    assert data.cell_3_voltage == 3.004
    assert data.cell_4_voltage == 3.006
    assert data.device_id == 0x0A
    assert data.bq4050_communication is True
    assert data.ip2368_communication is True
    assert data.control_register == 0x55
    assert data.configured_i2c_address == 0x2D
    assert data.watchdog_timeout == 10
    assert data.watchdog_startup_delay == 20
    assert data.software_revision == "V1.4"
