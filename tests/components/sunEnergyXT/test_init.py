from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.config_entries import ConfigEntryState
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.sunEnergyXT.const import DOMAIN

pytestmark = pytest.mark.asyncio

async def test_setup_entry(hass):
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            "serial_number": "DCBDCCC00562",
            "host": "10.6.50.106",
            "port": 8000,
            "device_name": "SunEnergyXT BK",
            "hw_version": "BK215",
            "sw_version": "V1.5.7",
        },
        title="SunEnergyXT BK",
    )
    entry.add_to_hass(hass)

    with (
        patch(
            "custom_components.sunEnergyXT.tcp_client.TcpClient.async_connect",
            new=AsyncMock(),
        ),
        patch(
            "custom_components.sunEnergyXT.tcp_client.TcpClient.async_stop_client",
            new=AsyncMock(),
        ),
        patch(
            "custom_components.sunEnergyXT.coordinator.SunEnergyXTCoordinator.async_config_entry_first_refresh",
            new=AsyncMock(),
        ),
        patch(
            "homeassistant.components.zeroconf.async_setup",
            return_value=True,
        ),
        patch(
            "homeassistant.components.dhcp.async_setup",
            return_value=True,
        ),
    ):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    assert entry.state is ConfigEntryState.LOADED
