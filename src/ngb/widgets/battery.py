from gi.repository import Gtk
from gi.repository import GLib

from ngb.modules import BatteryModule, WidgetBox


class Battery(WidgetBox):
    def __init__(self, **kwargs):
        self.timer = kwargs.get("timer", 5)
        self.icon_size = kwargs.get("icon_size", 20)
        self.battery = BatteryModule()
        super().__init__(timer=self.timer, icon_size=self.icon_size)

    def run(self):
        super().run()

    def set_text(self):
        battery_level = self.battery.get_battery_level()
        if battery_level == "":
            self.set_tooltip_text("No battery is found")
        self.icon = self.battery.get_battery_icon()
        self.text_label.set_label(battery_level)
        self.set_icon()
        return True
