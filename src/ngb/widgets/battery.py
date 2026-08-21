from gi.repository import Gtk
from gi.repository import GLib

from ngb.modules import BatteryModule, WidgetBox


class Battery(WidgetBox):
    def __init__(self, **kwargs):
        self.timer = kwargs.get("timer", 5)
        self.icon_size = kwargs.get("icon_size", 20)
        self.battery = BatteryModule()
        super().__init__(timer=self.timer, icon_size=self.icon_size)

    def _task_func(self, task, _task_data, _cancellable, _other):
        battery_level = self.battery.get_battery_level()
        if battery_level == "":
            data = {
                "icon": self.battery.get_battery_icon(),
                "tooltip": "No battery is found",
            }
        else:
            data = {"text": battery_level, "icon": self.battery.get_battery_icon()}
        task.return_value(data)
