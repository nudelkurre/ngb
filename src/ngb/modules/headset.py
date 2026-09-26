from shutil import which

import json
import subprocess
import re

from ngb.types import NamedTuples

HeadsetDevice = NamedTuples.HeadsetDevice


class HeadsetModule:
    def __init__(self, **kwargs):
        pass

    def get_headset_info(self):
        path = which("headsetcontrol")
        device_battery = []
        if path:
            try:
                info = json.loads(
                    subprocess.run(
                        "headsetcontrol -o JSON".split(),
                        capture_output=True,
                        text=True,
                        timeout=3,
                    ).stdout
                )
                for device in info.get("devices", []):
                    if device.get("battery", {}).get("level") > 0:
                        device_battery.append(
                            HeadsetDevice(
                                name=device.get("device", ""),
                                batterylevel=device.get("battery", {}).get("level", 0),
                                icon="󰋎",
                            )
                        )
            except subprocess.TimeoutExpired as e:
                device_battery.append(HeadsetDevice(icon="", error=-1))
        else:
            device_battery.append(HeadsetDevice(icon="", error=-2))
        return device_battery
