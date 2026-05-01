from gi.repository import Gtk
from gi.repository import GLib

from ngb.modules import HeadsetModule, WidgetBox


class Headset(WidgetBox):
    min_timer = 5

    def __init__(self, **kwargs):
        self.default_icon = "󰋎"
        self.warning_icon = ""
        self.icon = kwargs.get("icon", self.default_icon)
        self.timer = kwargs.get("timer", self.min_timer)
        if self.timer < self.min_timer:
            self.timer = self.min_timer
        self.icon_size = kwargs.get("icon_size", 20)
        self.headset = HeadsetModule()
        super().__init__(icon=self.icon, icon_size=self.icon_size, timer=self.timer)

    def run(self):
        super().run()

    def set_text(self):
        battery_levels = self.headset.get_headset_info()
        self.set_visible(True)
        if isinstance(battery_levels, list) and len(battery_levels) > 0:
            self.text_label.set_text(" ".join(battery_levels))
            self.icon = self.default_icon
            self.set_icon()
        elif battery_levels == -1:
            self.text_label.set_text("")
            self.set_tooltip_text("Process timed out")
            self.stop()
        elif battery_levels == -2:
            self.text_label.set_text("")
            self.set_tooltip_text("headsetcontrol not installed")
            self.icon = self.warning_icon
            self.set_icon()
        else:
            self.set_visible(False)
        return True
