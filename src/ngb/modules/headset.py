from shutil import which

import json
import subprocess
import re


class HeadsetModule:
    def __init__(self, **kwargs):
        pass

    def get_headset_info(self):
        path = which("headsetcontrol")
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
                device_battery = []
                for device in info.get("devices", []):
                    battery_level = device.get("battery", {}).get("level", 0)
                    if battery_level > 0:
                        device_battery.append(f"{battery_level}%")
                return device_battery
            except subprocess.TimeoutExpired as e:
                return -1
        else:
            return -2
