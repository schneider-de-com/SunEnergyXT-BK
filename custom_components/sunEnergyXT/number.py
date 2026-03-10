from __future__ import annotations

from homeassistant.components.number import NumberEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import NUMBER_DESCRIPTIONS, NumberDescription
from .coordinator import SunEnergyXTCoordinator
from .data_info import DataInfo, RequestInfo


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    runtime_data = entry.runtime_data
    coordinator: SunEnergyXTCoordinator = runtime_data.coordinator
    device_info = runtime_data.device_info
    client = runtime_data.client
    created: set[str] = set()

    def _add_entities() -> None:
        new_entities: list[SunEnergyXTNumber] = []
        for key, description in NUMBER_DESCRIPTIONS.items():
            if key not in coordinator.available_points or key in created:
                continue
            created.add(key)
            new_entities.append(
                SunEnergyXTNumber(
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


class SunEnergyXTNumber(CoordinatorEntity, NumberEntity):
    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(
        self,
        coordinator: SunEnergyXTCoordinator,
        client,
        serial_number: str,
        device_info,
        description: NumberDescription,
    ) -> None:
        super().__init__(coordinator)
        self.client = client
        self.entity_description = description
        self._point = description.key
        self._attr_unique_id = f"{serial_number}_{self._point}"
        self._attr_name = description.name
        self._attr_device_info = device_info
        self._attr_native_min_value = description.native_min_value
        self._attr_native_max_value = description.native_max_value
        self._attr_native_step = description.native_step
        self._attr_native_unit_of_measurement = description.native_unit_of_measurement
        self._attr_entity_category = description.entity_category

    @property
    def native_value(self):
        return self.coordinator.data.get(self._point)

    @property
    def available(self) -> bool:
        return self._point in self.coordinator.available_points

    @property
    def extra_state_attributes(self):
        return {"protocol_point": self._point}

    async def async_set_native_value(self, value: float) -> None:
        data_info = DataInfo()
        setattr(data_info, self._point, int(value))
        request_info = RequestInfo(code=0x6056, data=data_info)
        ok = await self.client.async_set_data(
            self._point, int(value), request_info.request_to_json_remove_FF()
        )
        if ok:
            await self.coordinator.async_request_refresh()
