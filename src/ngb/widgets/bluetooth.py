from gi.repository import Gtk
from gi.repository import GLib
import subprocess
import re

from ngb.modules import WidgetBox

class  Bluetooth(Gtk.Box):
    def __init__(self, timer=5000, spacing=10):
        super().__init__(spacing=spacing)
        self.timer = timer
        self.spacing = spacing
        self.update_boxes()
        self.update_list()

    def update_boxes(self):
        while self.get_first_accessible_child() is not None:
            self.remove(self.get_first_accessible_child())

        for device in self.get_devices():
            if(device["connected"]):
                self.append(WidgetBox(icon=device["icon"], text=f"{device['battery']}%", spacing=self.spacing))

        return True

    def get_devices(self):
        icons = {"input-gaming": "", "audio-headset": "󰋎"}
        devices = subprocess.run("bluetoothctl devices".split(), capture_output=True, text=True).stdout.split("\n")[:-1]

        dev_list = []
        for d in devices:
            match = re.search(r"Device\s([A-F0-9]{2}\:[A-F0-9]{2}\:[A-F0-9]{2}\:[A-F0-9]{2}\:[A-F0-9]{2}\:[A-F0-9]{2})\s([\w\s\d\(\)\-\.]+)", d)
            if(match):
                device = {"address": match.group(1), "name": match.group(2)}
                info = subprocess.run(f"bluetoothctl info {match.group(1)}".split(), capture_output=True, text=True).stdout.split("\n")
                for i in info:
                    if("Icon" in i):
                        device["icon"] = icons[re.match(r"\s*Icon:\s([\w\-]+)", i).group(1)]
                    elif("Battery Percentage" in i):
                        device["battery"] = re.match(r"\s*Battery\sPercentage:\s[0-9a-fx]{4}\s\(([\d]+)\)", i).group(1)
                    elif("Connected" in i):
                        device["connected"] = True if re.match(r"\s*Connected:\s([\w]+)", i).group(1) == "yes" else False

                if("icon" not in device):
                    device["icon"] = "󰥈"
                if(device["connected"]):
                    dev_list.append(device)
        print(dev_list)
        return (dev_list)

    def update_list(self):
        GLib.timeout_add(self.timer, self.update_boxes)
        return True