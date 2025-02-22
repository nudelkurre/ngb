from gi.repository import Gtk
from gi.repository import GLib
from datetime import datetime

from ngb.modules import WidgetBox

class Clock(WidgetBox):
    timeformat = ""
    def __init__(self, timeformat="%Y-%m-%d %H:%M:%S"):
        super().__init__(icon="", spacing=4)
        self.timeformat = timeformat

    def set_text(self):
        datetimenow = datetime.now().strftime(self.timeformat)
        self.text_label.set_text(datetimenow)
        return True