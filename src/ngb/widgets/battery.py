from gi.repository import Gtk
from gi.repository import GLib
import psutil
from psutil._common import bytes2human

from ngb.modules import WidgetBox


class Battery(WidgetBox):
    def __init__(self, **kwargs):
        self.timer = kwargs.get("timer", 5)
        self.icon = kwargs.get("icon", "󰁹")
        self.icon_size = kwargs.get("icon_size", 20)
        super().__init__(timer=self.timer, icon=self.icon, icon_size=self.icon_size)

    def set_text(self):
        self.get_battery_level()
        return True

    def get_battery_level(self):
        battery = psutil.sensors_battery()
        battery_level = int(battery.percent)
        charging = battery.power_plugged
        if charging:
            if battery_level == 100:
                self.icon = "󰚥"
            else:
                self.icon = "󰂄"
        else:
            self.icon = "󰁹"
        self.set_icon()
        self.text_label.set_label(f"{battery_level}%")
        return True

    def update_battery_level(self):
        GLib.timeout_add(self.timer, self.get_battery_level)
