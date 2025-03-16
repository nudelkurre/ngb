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
        self.icon_size = kwargs.get("icon_size", 20)
        self.mountpoint_label = Gtk.Label()
        self.storage_label = Gtk.Label()
        self.used_bar = Gtk.ProgressBar()
        super().__init__(timer=self.timer, icon=self.icon, icon_size=self.icon_size)
        self.populate_dropdown()

    def set_text(self):
        self.get_disk_usage()
        return True

    def populate_dropdown(self):
        self.dropdown.add(self.mountpoint_label)
        self.dropdown.add(self.used_bar)
        self.dropdown.add(self.storage_label)

    def get_disk_usage(self):
        disk_data = psutil.disk_usage(self.mountpoint)
        percent = disk_data.percent
        self.text_label.set_label(f"{percent}%")
        self.mountpoint_label.set_label(f"{self.mountpoint}")
        self.storage_label.set_label(f"{bytes2human(disk_data.used)}iB/{bytes2human(disk_data.total)}iB")
        self.used_bar.set_fraction(disk_data.used / disk_data.total)
        return True

    def update_disk_usage(self):
        GLib.timeout_add(self.timer, self.get_disk_usage)

    def on_click(self, user_data):
        self.dropdown.popup()
        return True