from __future__ import annotations

import json
from dataclasses import asdict, dataclass, fields
from typing import Any


@dataclass
class DataInfo:
    """Protocol data container."""

    t700_1: int = 0xFFFFFFFF
    t701_1: int = 0xFFFFFFFF
    t702_1: int = 0xFFFFFFFF
    t728: int = 0xFFFFFFFF
    t598: int = 0xFFFFFFFF
    t362: int = 0xFFFFFFFF
    t363: int = 0xFFFFFFFF
    t720: int = 0xFFFFFFFF
    t721: int = 0xFFFFFFFF
    t727: int = 0xFFFFFFFF
    t590: int = 0xFFFFFFFF
    t596: int = 0xFFFFFFFF
    t597: int = 0xFFFFFFFF
    t211: int = 0xFFFFFFFF
    t592: int = 0xFFFFFFFF
    t593: int = 0xFFFFFFFF
    t594: int = 0xFFFFFFFF
    t595: int = 0xFFFFFFFF
    t1001: int = 0xFFFFFFFF
    t1002: int = 0xFFFFFFFF
    t1003: int = 0xFFFFFFFF
    t1004: int = 0xFFFFFFFF
    t507: int = 0xFFFFFFFF
    t508: int = 0xFFFFFFFF
    t509: int = 0xFFFFFFFF
    t510: int = 0xFFFFFFFF
    t511: int = 0xFFFFFFFF
    t512: int = 0xFFFFFFFF
    t513: int = 0xFFFFFFFF
    t514: int = 0xFFFFFFFF
    t948: int = 0xFFFFFFFF
    t949: int = 0xFFFFFFFF
    t950: int = 0xFFFFFFFF
    t951: int = 0xFFFFFFFF
    t952: int = 0xFFFFFFFF
    t953: int = 0xFFFFFFFF
    t954: int = 0xFFFFFFFF
    t955: int = 0xFFFFFFFF
    t33: int = 0xFFFFFFFF
    t34: int = 0xFFFFFFFF
    t49: int = 0xFFFFFFFF
    t66: int = 0xFFFFFFFF
    t710: int = 0xFFFFFFFF
    t711: int = 0xFFFFFFFF
    t701_4: int = 0xFFFFFFFF
    t702_4: int = 0xFFFFFFFF
    t50: int = 0xFFFFFFFF
    t62: int = 0xFFFFFFFF
    t63: int = 0xFFFFFFFF
    t64: int = 0xFFFFFFFF
    t65: int = 0xFFFFFFFF
    t812: int = 0xFFFFFFFF
    t813: int = 0xFFFFFFFF
    t814: int = 0xFFFFFFFF
    t815: int = 0xFFFFFFFF
    t220: int = 0xFFFFFFFF
    t233: int = 0xFFFFFFFF
    t246: int = 0xFFFFFFFF
    t259: int = 0xFFFFFFFF
    t836: int = 0xFFFFFFFF
    t849: int = 0xFFFFFFFF
    t862: int = 0xFFFFFFFF
    t875: int = 0xFFFFFFFF
    t586: int = 0xFFFFFFFF
    t537: int = 0xFFFFFFFF
    t536: int = 0xFFFFFFFF
    t545: int = 0xFFFFFFFF
    t544: int = 0xFFFFFFFF
    t553: int = 0xFFFFFFFF
    t552: int = 0xFFFFFFFF
    t561: int = 0xFFFFFFFF
    t560: int = 0xFFFFFFFF
    t569: int = 0xFFFFFFFF
    t568: int = 0xFFFFFFFF
    t970: int = 0xFFFFFFFF
    t969: int = 0xFFFFFFFF
    t978: int = 0xFFFFFFFF
    t977: int = 0xFFFFFFFF
    t986: int = 0xFFFFFFFF
    t985: int = 0xFFFFFFFF
    t994: int = 0xFFFFFFFF
    t993: int = 0xFFFFFFFF
    t475: int = 0xFFFFFFFF
    M_ER1: int = 0xFFFFFFFF
    M_ER2: int = 0xFFFFFFFF
    M_ER3: int = 0xFFFFFFFF
    S2_ER1: int = 0xFFFFFFFF
    S2_ER2: int = 0xFFFFFFFF

    @classmethod
    def dict_to_data(cls, data_dict: dict[str, Any]) -> DataInfo:
        valid_fields = {field.name for field in fields(cls)}
        filtered = {
            key: value for key, value in data_dict.items() if key in valid_fields
        }
        return cls(**filtered)

    def data_to_json(self) -> str:
        return json.dumps(asdict(self), separators=(",", ":"))


@dataclass
class RequestInfo:
    code: int
    data: DataInfo

    def request_to_json_remove_FF(self) -> str:
        def remove_ffff(value: Any):
            if isinstance(value, dict):
                return {k: remove_ffff(v) for k, v in value.items() if v != 0xFFFFFFFF}
            if isinstance(value, list):
                return [remove_ffff(item) for item in value]
            return value

        filtered = remove_ffff(asdict(self))
        return json.dumps(filtered, separators=(",", ":"))


@dataclass
class DiagnosticInfo:
    connection: str = ""
    reporttime: str = ""
    networkrssi: str = ""

@dataclass
class MdnsDeiveInfo:
    """mDNS device discovery info."""

    service_type: str
    service_name: str
    serial_number: str
    host: str
    port: int
    sw_version: str
    hw_version: str