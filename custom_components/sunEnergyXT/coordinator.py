from __future__ import annotations

from collections.abc import Callable
from datetime import timedelta
import logging
from typing import Any

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import INVALID_VALUES, POLL_INTERVAL_SECONDS, POLL_REQUESTS

_LOGGER = logging.getLogger(__name__)


class SunEnergyXTCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator for SunEnergyXT BK."""

    def __init__(self, hass, client) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name="sunEnergyXT",
            update_interval=timedelta(seconds=POLL_INTERVAL_SECONDS),
        )
        self.client = client
        self.available_points: set[str] = set()
        self._point_valid_hits: dict[str, int] = {}
        self._listeners: list[Callable[[], None]] = []

    def register_new_point_listener(self, listener: Callable[[], None]) -> Callable[[], None]:
        self._listeners.append(listener)

        def _remove() -> None:
            if listener in self._listeners:
                self._listeners.remove(listener)

        return _remove

    async def _async_update_data(self) -> dict[str, Any]:
        merged: dict[str, Any] = {}
        old_points = set(self.available_points)

        try:
            for payload in POLL_REQUESTS:
                await self.client.async_send_json(payload)
                messages = await self.client.read_messages(timeout=1.0)
                for message in messages:
                    data = message.get("data", {})
                    if isinstance(data, dict):
                        merged.update(data)

            self._update_available_points(merged)
            if self.available_points - old_points:
                for listener in list(self._listeners):
                    listener()
            return merged
        except Exception as err:
            raise UpdateFailed(f"Failed to update SunEnergyXT data: {err}") from err

    def _update_available_points(self, data: dict[str, Any]) -> None:
        for key, value in data.items():
            if not self._is_valid_value(value):
                continue
            self._point_valid_hits[key] = self._point_valid_hits.get(key, 0) + 1
            if self._point_valid_hits[key] >= 2:
                self.available_points.add(key)

    @staticmethod
    def _is_valid_value(value: Any) -> bool:
        if value in INVALID_VALUES:
            return False
        if isinstance(value, str) and not value.strip():
            return False
        return isinstance(value, (int, float, str, bool))
