from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import EntityCategory

DOMAIN = "sunEnergyXT"

POLL_INTERVAL_SECONDS = 15
POLL_REQUESTS = (
    {"code": 0x6052},
    {"code": 0x6055},
    {"code": 0x6059},
)

INVALID_VALUES = {-1, 0xFFFFFFFF, "", None}


@dataclass(frozen=True, slots=True)
class SensorDescription:
    key: str
    name: str
    native_unit_of_measurement: str | None = None
    device_class: SensorDeviceClass | None = None
    state_class: SensorStateClass | None = None
    entity_category: EntityCategory | None = None
    suggested_display_precision: int | None = None
    multiplier: float = 1.0
    offset: float = 0.0


@dataclass(frozen=True, slots=True)
class NumberDescription:
    key: str
    name: str
    native_min_value: float
    native_max_value: float
    native_step: float
    native_unit_of_measurement: str | None = None
    entity_category: EntityCategory | None = None


@dataclass(frozen=True, slots=True)
class SwitchDescription:
    key: str
    name: str
    entity_category: EntityCategory | None = None


def _unit_label(index: int) -> str:
    return "Head Unit" if index == 0 else f"Expansion {index}"


SENSOR_DESCRIPTIONS: dict[str, SensorDescription] = {
    "t211": SensorDescription(
        key="t211",
        name="System SOC",
        native_unit_of_measurement="%",
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
    ),
    "t33": SensorDescription(
        key="t33",
        name="Total Input Power",
        native_unit_of_measurement="W",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
    ),
    "t34": SensorDescription(
        key="t34",
        name="Total Output Power",
        native_unit_of_measurement="W",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
    ),
    "t49": SensorDescription(
        key="t49",
        name="Daily PV Energy",
        native_unit_of_measurement="kWh",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=2,
        multiplier=0.01,
    ),
    "t66": SensorDescription(
        key="t66",
        name="Daily Output Energy",
        native_unit_of_measurement="kWh",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=2,
        multiplier=0.01,
    ),
    "t710": SensorDescription(
        key="t710",
        name="Daily AC Charging Energy",
        native_unit_of_measurement="kWh",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=2,
        multiplier=0.01,
    ),
    "t711": SensorDescription(
        key="t711",
        name="AC Input Power",
        native_unit_of_measurement="W",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
    ),
    "t701_4": SensorDescription(
        key="t701_4",
        name="EV Mode Power",
        native_unit_of_measurement="W",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
    ),
    "t702_4": SensorDescription(
        key="t702_4",
        name="Home Mode Power",
        native_unit_of_measurement="W",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
    ),
    "t475": SensorDescription(
        key="t475",
        name="Network RSSI",
        native_unit_of_measurement="dB",
        entity_category=EntityCategory.DIAGNOSTIC,
        suggested_display_precision=0,
        multiplier=-1,
    ),
    "M_ER1": SensorDescription(
        key="M_ER1", name="Head Unit Error 1", entity_category=EntityCategory.DIAGNOSTIC
    ),
    "M_ER2": SensorDescription(
        key="M_ER2", name="Head Unit Error 2", entity_category=EntityCategory.DIAGNOSTIC
    ),
    "M_ER3": SensorDescription(
        key="M_ER3", name="Head Unit Error 3", entity_category=EntityCategory.DIAGNOSTIC
    ),
    "S2_ER1": SensorDescription(
        key="S2_ER1",
        name="Expansion Error 1",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    "S2_ER2": SensorDescription(
        key="S2_ER2",
        name="Expansion Error 2",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
}

NUMBER_DESCRIPTIONS: dict[str, NumberDescription] = {
    "t362": NumberDescription("t362", "Minimum Discharge SOC", 1, 20, 1, "%"),
    "t363": NumberDescription("t363", "Maximum Charge SOC", 70, 100, 1, "%"),
    "t720": NumberDescription("t720", "Home Mode Minimum SOC", 5, 20, 1, "%"),
    "t721": NumberDescription("t721", "EV Mode Minimum SOC", 5, 40, 1, "%"),
    "t727": NumberDescription("t727", "Charge Mode Maximum SOC", 80, 100, 1, "%"),
    "t590": NumberDescription("t590", "Configured Charge Power", 0, 3600, 1, "W"),
    "t596": NumberDescription("t596", "No Input Output Timeout", 15, 1440, 1, "min"),
    "t597": NumberDescription("t597", "DOD Timeout", 5, 1440, 1, "min"),
}

SWITCH_DESCRIPTIONS: dict[str, SwitchDescription] = {
    "t598": SwitchDescription("t598", "Local Communication"),
    "t700_1": SwitchDescription("t700_1", "Charge Mode"),
    "t701_1": SwitchDescription("t701_1", "EV Mode"),
    "t702_1": SwitchDescription("t702_1", "Home Mode"),
    "t728": SwitchDescription("t728", "AC Mix In EV Mode"),
}

SOC_POINTS = {
    0: "t592",
    1: "t593",
    2: "t594",
    3: "t595",
    4: "t1001",
    5: "t1002",
    6: "t1003",
    7: "t1004",
}
LIMIT_MIN_POINTS = {
    0: "t507",
    1: "t509",
    2: "t511",
    3: "t513",
    4: "t948",
    5: "t950",
    6: "t952",
    7: "t954",
}
LIMIT_MAX_POINTS = {
    0: "t508",
    1: "t510",
    2: "t512",
    3: "t514",
    4: "t949",
    5: "t951",
    6: "t953",
    7: "t955",
}
CELLTEMP_POINTS = {
    0: "t220",
    1: "t233",
    2: "t246",
    3: "t259",
    4: "t836",
    5: "t849",
    6: "t862",
    7: "t875",
}
PV_POWER_POINTS = {
    0: ("t50", "Head Unit PV1 Input Power"),
    1: ("t62", "Head Unit PV2 Input Power"),
    2: ("t63", "Expansion 1 PV Input Power"),
    3: ("t64", "Expansion 2 PV Input Power"),
    4: ("t65", "Expansion 3 PV Input Power"),
    5: ("t812", "Expansion 4 PV Input Power"),
    6: ("t813", "Expansion 5 PV Input Power"),
    7: ("t814", "Expansion 6 PV Input Power"),
    8: ("t815", "Expansion 7 PV Input Power"),
}
MPPT_VOLTAGE_POINTS = {
    0: ("t536", "Head Unit MPPT1 Voltage"),
    1: ("t544", "Head Unit MPPT2 Voltage"),
    2: ("t552", "Expansion 1 MPPT Voltage"),
    3: ("t560", "Expansion 2 MPPT Voltage"),
    4: ("t568", "Expansion 3 MPPT Voltage"),
    5: ("t969", "Expansion 4 MPPT Voltage"),
    6: ("t977", "Expansion 5 MPPT Voltage"),
    7: ("t985", "Expansion 6 MPPT Voltage"),
    8: ("t993", "Expansion 7 MPPT Voltage"),
}
MPPT_CURRENT_POINTS = {
    0: ("t537", "Head Unit MPPT1 Current"),
    1: ("t545", "Head Unit MPPT2 Current"),
    2: ("t553", "Expansion 1 MPPT Current"),
    3: ("t561", "Expansion 2 MPPT Current"),
    4: ("t569", "Expansion 3 MPPT Current"),
    5: ("t970", "Expansion 4 MPPT Current"),
    6: ("t978", "Expansion 5 MPPT Current"),
    7: ("t986", "Expansion 6 MPPT Current"),
    8: ("t994", "Expansion 7 MPPT Current"),
}

for index, point in SOC_POINTS.items():
    SENSOR_DESCRIPTIONS[point] = SensorDescription(
        key=point,
        name=f"{_unit_label(index)} SOC",
        native_unit_of_measurement="%",
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
    )

for index, point in LIMIT_MIN_POINTS.items():
    SENSOR_DESCRIPTIONS[point] = SensorDescription(
        key=point,
        name=f"{_unit_label(index)} Minimum SOC Limit",
        native_unit_of_measurement="%",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
    )

for index, point in LIMIT_MAX_POINTS.items():
    SENSOR_DESCRIPTIONS[point] = SensorDescription(
        key=point,
        name=f"{_unit_label(index)} Maximum SOC Limit",
        native_unit_of_measurement="%",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
    )

for index, point in CELLTEMP_POINTS.items():
    SENSOR_DESCRIPTIONS[point] = SensorDescription(
        key=point,
        name=f"{_unit_label(index)} Cell Temperature",
        native_unit_of_measurement="°C",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
    )

for _, (point, name) in PV_POWER_POINTS.items():
    SENSOR_DESCRIPTIONS[point] = SensorDescription(
        key=point,
        name=name,
        native_unit_of_measurement="W",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
    )

for _, (point, name) in MPPT_VOLTAGE_POINTS.items():
    SENSOR_DESCRIPTIONS[point] = SensorDescription(
        key=point,
        name=name,
        native_unit_of_measurement="V",
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        multiplier=0.1,
    )

for _, (point, name) in MPPT_CURRENT_POINTS.items():
    SENSOR_DESCRIPTIONS[point] = SensorDescription(
        key=point,
        name=name,
        native_unit_of_measurement="A",
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        multiplier=0.1,
    )
