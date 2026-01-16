from collections import namedtuple


class NamedTuples:
    Workspace = namedtuple(
        "Workspace",
        ["id", "name", "focused", "output", "urgent"],
        defaults=(0, "", False, "", False),
    )

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
        ["temperature", "temperature_unit", "windspeed", "weather_code", "icon"],
        defaults=(0, "C", 0.0, 1, ""),
    )
