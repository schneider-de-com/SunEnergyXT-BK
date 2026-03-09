from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import SWITCH_DESCRIPTIONS, SwitchDescription
from .coordinator import SunEnergyXTCoordinator
from .data_info import DataInfo, RequestInfo


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    runtime_data = entry.runtime_data
    coordinator: SunEnergyXTCoordinator = runtime_data.coordinator
    device_info = runtime_data.device_info
    client = runtime_data.client
    created: set[str] = set()

    def _add_entities() -> None:
        new_entities: list[SunEnergyXTSwitch] = []
        for key, description in SWITCH_DESCRIPTIONS.items():
            if key not in coordinator.available_points or key in created:
                continue
            created.add(key)
            new_entities.append(
                SunEnergyXTSwitch(
                    coordinator=coordinator,
                    client=client,
                    serial_number=entry.data["serial_number"],
                    device_info=device_info,
                    description=description,
                )
            )
        if new_entities:
            async_add_entities(new_entities)

    _add_entities()
    entry.async_on_unload(coordinator.register_new_point_listener(_add_entities))


class SunEnergyXTSwitch(CoordinatorEntity, SwitchEntity):
    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, coordinator: SunEnergyXTCoordinator, client, serial_number: str, device_info, description: SwitchDescription) -> None:
        super().__init__(coordinator)
        self.client = client
        self.entity_description = description
        self._point = description.key
        self._attr_unique_id = f"{serial_number}_{self._point}"
        self._attr_name = description.name
        self._attr_device_info = device_info
        self._attr_entity_category = description.entity_category

    @property
    def is_on(self) -> bool | None:
        return self.coordinator.data.get(self._point) == 1

    @property
    def available(self) -> bool:
        return self._point in self.coordinator.available_points

    @property
    def extra_state_attributes(self):
        return {"protocol_point": self._point}

    async def async_turn_on(self, **kwargs) -> None:
        await self._async_set_value(1)

    async def async_turn_off(self, **kwargs) -> None:
        await self._async_set_value(0)

    async def _async_set_value(self, value: int) -> None:
        data_info = DataInfo()
        setattr(data_info, self._point, value)
        request_info = RequestInfo(code=0x6056, data=data_info)
        ok = await self.client.async_set_data(self._point, value, request_info.request_to_json_remove_FF())
        if ok:
            await self.coordinator.async_request_refresh()
