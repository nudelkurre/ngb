from collections import namedtuple
from dataclasses import dataclass, field


class NamedTuples:
    @dataclass
    class Workspace:
        id: int = 0
        name: str = ""
        focused: bool = False
        output: str = ""
        urgent: bool = False
        active: bool = False

    @dataclass
    class Window:
        id: int = 0
        title: str = ""
        focused: bool = False

    @dataclass
    class Monitor:
        name: str = ""
        active: bool = False
        workspaces: list[int] = field(default_factory=list)
        active_workspace: int = 0

    BluetoothDevice = namedtuple(
        "BluetoothDevice",
        ["adapter", "address", "battery", "connected", "icon", "name"],
        defaults=("", "", "", False, "󰥈", ""),
    )

    VolumeSink = namedtuple(
        "VolumeSink",
        ["id", "name", "volume", "muted", "default"],
        defaults=(0, "", 0.0, False, False),
    )

    Weather = namedtuple(
        "Weather",
        [
            "temperature",
            "temperature_unit",
            "windspeed",
            "weather_code",
            "icon",
            "error",
        ],
        defaults=(0, "C", 0.0, 1, "", None),
    )

    DiskInfo = namedtuple(
        "DiskInfo", ["percentage", "used", "total"], defaults=("0%", "0iB", "0iB")
    )

    HeadsetDevice = namedtuple(
        "HeadsetDevice",
        ["name", "batterylevel", "icon", "error"],
        defaults=("", 0, "?", None),
    )
