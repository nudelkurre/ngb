from gi.repository import Gtk
from gi.repository import GLib
from datetime import datetime

class Clock(Gtk.Label):
    label = ""
    timeformat = ""
    def __init__(self, timeformat):
        Gtk.Label.__init__(self, label=self.label)
        self.timeformat = timeformat
        self.displayClock()
        self.startclocktimer()

    def displayClock(self):
        datetimenow = datetime.now().strftime(self.timeformat)
        self.set_text(datetimenow)
        return True

    def startclocktimer(self):
        GLib.timeout_add(1000, self.displayClock)