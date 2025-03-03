from gi.repository import Gtk
from gi.repository import GLib
from shutil import which

import json
import subprocess
import re

from ngb.modules import WidgetBox

class Headset(WidgetBox):
    def __init__(self):
        self.icon = "󰋎"
        super().__init__(icon=self.icon)

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