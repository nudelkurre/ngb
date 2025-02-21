from gi.repository import Gtk
from gi.repository import GLib
from datetime import datetime

from ngb.modules import WidgetBox

class Clock(WidgetBox):
    label = ""
    timeformat = ""
    text_label = Gtk.Label()
    icon_label = Gtk.Label()

    def __init__(self, timeformat="%Y-%m-%d %H:%M:%S"):
        WidgetBox.__init__(self, icon="", spacing=4)
        self.timeformat = timeformat

    def set_text(self):
        datetimenow = datetime.now().strftime(self.timeformat)
        self.text_label.set_text(datetimenow)
        return True