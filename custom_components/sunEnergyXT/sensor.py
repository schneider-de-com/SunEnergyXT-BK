from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import SENSOR_DESCRIPTIONS, SensorDescription
from .coordinator import SunEnergyXTCoordinator


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    runtime_data = entry.runtime_data
    coordinator: SunEnergyXTCoordinator = runtime_data.coordinator
    device_info = runtime_data.device_info
    created: set[str] = set()

    def _add_entities() -> None:
        new_entities: list[SunEnergyXTSensor] = []
        for key, description in SENSOR_DESCRIPTIONS.items():
            if key not in coordinator.available_points or key in created:
                continue
            created.add(key)
            new_entities.append(
                SunEnergyXTSensor(
                    coordinator=coordinator,
                    serial_number=entry.data["serial_number"],
                    device_info=device_info,
                    description=description,
                )
            )
        if new_entities:
            async_add_entities(new_entities)

    _add_entities()
    entry.async_on_unload(coordinator.register_new_point_listener(_add_entities))


class SunEnergyXTSensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, coordinator: SunEnergyXTCoordinator, serial_number: str, device_info, description: SensorDescription) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._point = description.key
        self._attr_unique_id = f"{serial_number}_{self._point}"
        self._attr_name = description.name
        self._attr_device_info = device_info
        self._attr_native_unit_of_measurement = description.native_unit_of_measurement
        self._attr_device_class = description.device_class
        self._attr_state_class = description.state_class
        self._attr_entity_category = description.entity_category
        self._attr_suggested_display_precision = description.suggested_display_precision

    @property
    def native_value(self):
        value = self.coordinator.data.get(self._point)
        if value is None:
            return None
        description = self.entity_description
        if isinstance(value, (int, float)):
            converted = (value * description.multiplier) + description.offset
            precision = description.suggested_display_precision
            return round(converted, precision) if precision is not None else converted
        return value

    @property
    def available(self) -> bool:
        return self._point in self.coordinator.available_points

    @property
    def extra_state_attributes(self):
        return {"protocol_point": self._point}
