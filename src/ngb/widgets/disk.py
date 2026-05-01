from gi.repository import Gtk
from gi.repository import GLib

from ngb.modules import DiskModule, WidgetBox


class Disk(WidgetBox):
    def __init__(self, **kwargs):
        self.mountpoint = kwargs.get("mountpoint", "/")
        self.icon = kwargs.get("icon", "")
        self.timer = kwargs.get("timer", 10)
        self.icon_size = kwargs.get("icon_size", 20)
        self.mountpoint_label = Gtk.Label(label=self.mountpoint)
        self.storage_label = Gtk.Label()
        self.used_bar = Gtk.ProgressBar()
        self.disk_info = DiskModule(mountpoint=self.mountpoint)
        super().__init__(timer=self.timer, icon=self.icon, icon_size=self.icon_size)

    def run(self):
        super().run()
        self.populate_dropdown()

    def set_text(self):
        disk_usage = self.disk_info.get_disk_usage()
        self.text_label.set_label(disk_usage.percentage)
        self.storage_label.set_label(f"{disk_usage.used}/{disk_usage.total}")
        self.used_bar.set_fraction(self.disk_info.get_used_fraction())
        return True

    def populate_dropdown(self):
        self.dropdown.add(self.mountpoint_label)
        self.dropdown.add(self.used_bar)
        self.dropdown.add(self.storage_label)

    def on_click(self, user_data):
        self.dropdown.popup()
        return True
