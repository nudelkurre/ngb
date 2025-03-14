from gi.repository import Gtk
from gi.repository import GLib
import psutil
from psutil._common import bytes2human

from ngb.modules import WidgetBox

class Cpu(WidgetBox):
    def __init__(self, **kwargs):
        self.timer = kwargs.get("timer", 2)
        self.icon = kwargs.get("icon", "")
        super().__init__(timer=self.timer, icon=self.icon)

    def set_text(self):
        self.get_cpu_usage()
        return True

    def get_cpu_usage(self):
        usage = psutil.cpu_percent()
        self.text_label.set_label(f"{usage}%")
        return True

    def update_disk_usage(self):
        GLib.timeout_add(self.timer, self.get_cpu_usage)