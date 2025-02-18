from gi.repository import Gtk
from gi.repository import GLib
import psutil
from psutil._common import bytes2human

from pybar.modules import WidgetBox

class Disk(WidgetBox):
    mountpoint = ""
    text_label = Gtk.Label()
    icon_label = Gtk.Label()

    def __init__(self, mountpoint):
        self.mountpoint = mountpoint
        WidgetBox.__init__(self, timer=10000, icon="")

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