from __future__ import annotations

import pytest

from custom_components.sunEnergyXT.number import async_setup_entry

pytestmark = pytest.mark.asyncio


class DummyCoordinator:
    def __init__(self, data: dict, available_points: set[str]) -> None:
        self.data = data
        self.available_points = available_points
        self._listeners: list = []

    def register_new_point_listener(self, listener):
        self._listeners.append(listener)

        def _remove():
            if listener in self._listeners:
                self._listeners.remove(listener)

        return _remove

    async def async_request_refresh(self):
        return None


class DummyClient:
    async def async_set_data(self, *args, **kwargs):
        return True


class DummyRuntimeData:
    def __init__(self, coordinator, client, device_info) -> None:
        self.coordinator = coordinator
        self.client = client
        self.device_info = device_info


class DummyEntry:
    def __init__(self, serial_number: str, runtime_data) -> None:
        self.data = {"serial_number": serial_number}
        self.runtime_data = runtime_data
        self._unload_callbacks = []

    def async_on_unload(self, callback):
        self._unload_callbacks.append(callback)


async def test_number_setup_creates_only_available_number_entities():
    coordinator = DummyCoordinator(
        data={
            "t590": 3600,
            "t362": 10,
            "t211": 100,
        },
        available_points={"t590", "t362"},
    )

    entry = DummyEntry(
        serial_number="DCBDCCC00562",
        runtime_data=DummyRuntimeData(
            coordinator=coordinator,
            client=DummyClient(),
            device_info={"identifiers": {("sunEnergyXT", "DCBDCCC00562")}},
        ),
    )

    added_entities = []

    def async_add_entities(entities):
        added_entities.extend(entities)

    await async_setup_entry(None, entry, async_add_entities)

    created_points = {entity._point for entity in added_entities}

    assert "t590" in created_points
    assert "t362" in created_points
    assert "t211" not in created_points