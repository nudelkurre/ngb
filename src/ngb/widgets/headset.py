from gi.repository import Gtk
from gi.repository import GLib
from shutil import which

import json
import subprocess
import re

from ngb.modules import WidgetBox

class Headset(WidgetBox):
    def __init__(self, **kwargs):
        self.icon = kwargs.get("icon", "󰋎")
        self.timer = kwargs.get("timer", 5)
        self.icon_size = kwargs.get("icon_size", 20)
        super().__init__(icon=self.icon, icon_size=self.icon_size, timer=self.timer)

    def set_text(self):
        path = which("headsetcontrol")
        if(path):
            info = json.loads(subprocess.run("headsetcontrol -o JSON".split(), capture_output=True, text=True).stdout)
            device_battery = []
            for d in info["devices"]:
                if(d["battery"]["level"] > 0):
                    device_battery.append(f"{d['battery']['level']}%")
            if(len(device_battery) > 0):
                self.set_visible(True)
            else:
                self.set_visible(False)
            self.text_label.set_text(" ".join(device_battery))
        else:
            self.text_label.set_text("headsetcontrol not installed")
        return True