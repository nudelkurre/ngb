from gi.repository import Gtk
from gi.repository import GLib
import psutil
from psutil._common import bytes2human

from ngb.modules import WidgetBox

class Disk(WidgetBox):
    def __init__(self, **kwargs):
        self.mountpoint = kwargs.get("mountpoint", "/")
        self.icon = kwargs.get("icon", "")
        self.timer = kwargs.get("timer", 10)
        super().__init__(timer=self.timer, icon=self.icon)

    def set_text(self):
        self.get_disk_usage()
        return True

    def get_disk_usage(self):
        disk_data = psutil.disk_usage(self.mountpoint)
        percent = disk_data.percent
        self.text_label.set_label(f"{percent}%")
        return True

    def update_disk_usage(self):
        GLib.timeout_add(self.timer, self.get_disk_usage)