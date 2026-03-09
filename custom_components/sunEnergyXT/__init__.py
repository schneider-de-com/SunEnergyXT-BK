from __future__ import annotations

from dataclasses import dataclass

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN
from .coordinator import SunEnergyXTCoordinator
from .tcp_client import TcpClient

PLATFORMS = [Platform.SENSOR, Platform.NUMBER, Platform.SWITCH]


@dataclass
class SunEnergyXTRuntimeData:
    client: TcpClient
    coordinator: SunEnergyXTCoordinator
    device_info: DeviceInfo


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    client = TcpClient(hass, entry)
    await client.async_connect()

    coordinator = SunEnergyXTCoordinator(hass, client)
    await coordinator.async_config_entry_first_refresh()

    device_info = DeviceInfo(
        identifiers={(DOMAIN, entry.data["serial_number"])},
        name=entry.title or entry.data.get("device_name") or "SunEnergyXT-BK",
        manufacturer="SunEnergyXT",
        model=entry.data.get("hw_version"),
        sw_version=entry.data.get("sw_version"),
        serial_number=entry.data.get("serial_number"),
    )

    entry.runtime_data = SunEnergyXTRuntimeData(
        client=client,
        coordinator=coordinator,
        device_info=device_info,
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    hass.data[DOMAIN][entry.entry_id] = entry.runtime_data
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    runtime_data: SunEnergyXTRuntimeData = entry.runtime_data
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    await runtime_data.client.async_stop_client()
    hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok
