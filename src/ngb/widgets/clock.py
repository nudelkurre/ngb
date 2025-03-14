from gi.repository import Gtk
from gi.repository import GLib
from datetime import datetime

from ngb.modules import WidgetBox

class Clock(WidgetBox):
    timeformat = ""
    def __init__(self, **kwargs):
        self.icon = kwargs.get("icon", "")
        self.spacing = kwargs.get("spacing", 4)
        self.timer = kwargs.get("timer", 1)
        self.timeformat = kwargs.get("timeformat_normal", "%T")
        self.timeformat_normal = kwargs.get("timeformat_normal", "%T")
        self.timeformat_hover = kwargs.get("timeformat_hover", "%Y-%m-%d %H:%M:%S")
        super().__init__(icon=self.icon, spacing=self.spacing, timer=self.timer)

    def set_text(self):
        datetimenow = datetime.now().strftime(self.timeformat)
        self.text_label.set_text(datetimenow)
        return True

    def on_hover_enter(self, controller, x, y):
        self.timeformat = self.timeformat_hover
        self.set_text()

    def on_hover_leave(self, controller):
        self.timeformat = self.timeformat_normal
        self.set_text()
