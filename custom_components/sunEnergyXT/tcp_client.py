from __future__ import annotations

import asyncio
import json
import logging
import re
import time

_LOGGER = logging.getLogger(__name__)

_MALFORMED_KEY_PATTERN = re.compile(r'""([A-Za-z0-9_ ]+)":')


class TcpClient:
    """Low-level TCP client for SunEnergyXT."""

    def __init__(self, hass, entry) -> None:
        self.hass = hass
        self.host = entry.data["host"]
        self.port = entry.data["port"]
        self.entry_id = entry.entry_id
        self.serial_number = entry.data["serial_number"]
        self.reader = None
        self.writer = None
        self.connected = False
        self._buffer = ""

    async def async_connect(self) -> None:
        await self.async_disconnect()
        self.reader, self.writer = await asyncio.wait_for(
            asyncio.open_connection(self.host, self.port),
            timeout=3.0,
        )
        self.connected = True
        _LOGGER.info("Connected to %s:%s", self.host, self.port)

    async def async_disconnect(self) -> None:
        self.connected = False
        self._buffer = ""
        if self.writer is not None:
            try:
                self.writer.close()
                await asyncio.wait_for(self.writer.wait_closed(), timeout=2.0)
            except Exception as err:
                _LOGGER.debug("Error closing writer: %s", err)
        self.reader = None
        self.writer = None

    async def async_stop_client(self) -> None:
        await self.async_disconnect()

    async def async_send_json(self, payload: dict) -> bool:
        if not self.connected or self.writer is None:
            return False
        try:
            raw = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
            _LOGGER.debug("%s send_data:%s", self.serial_number, raw)
            self.writer.write(raw.encode("ascii", errors="ignore"))
            await self.writer.drain()
            return True
        except Exception as err:
            _LOGGER.error("async_send_json_error: %s", err)
            self.connected = False
            return False

    async def async_set_data(self, data_type: str, data_value: int | float, set_data: str) -> bool:
        del data_value
        if not self.connected or self.writer is None:
            return False
        try:
            self.writer.write(set_data.encode("ascii", errors="ignore"))
            await self.writer.drain()
        except Exception as err:
            _LOGGER.error("async_set_data send error: %s", err)
            self.connected = False
            return False

        timeout = 2.0
        start = time.monotonic()
        while time.monotonic() - start <= timeout:
            messages = await self.read_messages(timeout=0.25)
            for msg in messages:
                code = msg.get("code")
                data = msg.get("data", {})
                if not isinstance(data, dict):
                    continue
                response_value = data.get(data_type)
                if code in {0, 0x6057} and response_value == 0:
                    return True
            await asyncio.sleep(0.05)
        return False

    async def read_messages(self, timeout: float = 1.0) -> list[dict]:
        if not self.connected or self.reader is None:
            return []
        end_time = asyncio.get_running_loop().time() + timeout
        messages: list[dict] = []
        while asyncio.get_running_loop().time() < end_time:
            try:
                chunk = await asyncio.wait_for(self.reader.read(4096), timeout=0.25)
                if not chunk:
                    self.connected = False
                    break
                decoded = chunk.decode("ascii", errors="ignore")
                _LOGGER.debug("%s receive_data:%s", self.serial_number, decoded)
                for raw_message in self._extract_json_messages(decoded):
                    parsed = self._parse_json_message(raw_message)
                    if parsed is not None:
                        messages.append(parsed)
            except TimeoutError:
                continue
            except asyncio.TimeoutError:
                continue
            except Exception as err:
                _LOGGER.error("read_messages_error: %s", err)
                break
        return messages

    def _extract_json_messages(self, chunk: str) -> list[str]:
        self._buffer += chunk
        messages: list[str] = []
        start_index = None
        depth = 0
        in_string = False
        escape = False
        for index, char in enumerate(self._buffer):
            if start_index is None:
                if char == "{":
                    start_index = index
                    depth = 1
                    in_string = False
                    escape = False
                continue
            if in_string:
                if escape:
                    escape = False
                elif char == "\\":
                    escape = True
                elif char == '"':
                    in_string = False
                continue
            if char == '"':
                in_string = True
            elif char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    messages.append(self._buffer[start_index : index + 1])
                    start_index = None
        if start_index is None:
            self._buffer = ""
        else:
            self._buffer = self._buffer[start_index:]
            if len(self._buffer) > 8192:
                self._buffer = self._buffer[-8192:]
        return messages

    def _parse_json_message(self, raw_message: str) -> dict | None:
        try:
            sanitized = _MALFORMED_KEY_PATTERN.sub(r'"\1":', raw_message)
            payload = json.loads(sanitized)
            if not isinstance(payload, dict):
                return None
            code = payload.get("code")
            data = payload.get("data", {})
            if not isinstance(data, dict):
                data = {}
            return {"code": code, "data": data}
        except Exception as err:
            _LOGGER.debug("Ignoring malformed frame %s: %s", raw_message, err)
            return None
