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

    def run(self):
        super().run()

    def set_text(self):
        self.get_battery_level()
        return True

    def get_battery_level(self):
        battery = psutil.sensors_battery()
        if battery == None:
            self.icon = "󱃍"
            self.set_icon()
            self.text_label.set_text("-")
            return True
        battery_level = int(battery.percent)
        charging = battery.power_plugged
        if charging:
            if battery_level == 100:
                self.icon = "󰚥"
            elif battery_level >= 75:
                self.icon = "󱊦"
            elif battery_level >= 50:
                self.icon = "󱊥"
            elif battery_level >= 25:
                self.icon = "󱊤"
            else:
                self.icon = "󰢟"
        else:
            if battery_level >= 75:
                self.icon = "󱊣"
            elif battery_level >= 50:
                self.icon = "󱊢"
            elif battery_level >= 25:
                self.icon = "󱊡"
            else:
                self.icon = "󰂎"
        self.set_icon()
        self.text_label.set_label(f"{battery_level}%")
        return True

    def update_battery_level(self):
        GLib.timeout_add(self.timer, self.get_battery_level)
