from gi.repository import Gtk
from gi.repository import GLib
from datetime import datetime

from ngb.modules import WidgetBox

class Clock(WidgetBox):
    timeformat = ""
    def __init__(self, timeformat_normal="%T", timeformat_hover="%Y-%m-%d %H:%M:%S"):
        super().__init__(icon="", spacing=4, timer=1000)
        self.timeformat = timeformat_normal
        self.timeformat_normal = timeformat_normal
        self.timeformat_hover = timeformat_hover

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
