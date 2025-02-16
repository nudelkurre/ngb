from gi.repository import Gtk
from gi.repository import GLib
import psutil
from psutil._common import bytes2human

class Disk(Gtk.Box):
    mountpoint: str = ""
    label = Gtk.Label()

    def __init__(self, mountpoint):
        self.mountpoint = mountpoint
        Gtk.Box.__init__(self)
        self.append(self.label)
        self.get_disk_usage()
        self.update_disk_usage()


    def get_disk_usage(self):
        disk_data = psutil.disk_usage(self.mountpoint)
        percent = disk_data.percent
        total = bytes2human(disk_data.total)
        used = bytes2human(disk_data.used)
        self.label.set_label(f"{used}/{total} {percent}%")
        return True

    def get_disk_total(self):
        disk_data = psutil.disk_usage(self.mountpoint)
        self.label.set_label(f"{used}/{total}")
        return True

    def update_disk_usage(self):
        GLib.timeout_add(10000, self.get_disk_usage)