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

    def _task_func(self, task, _task_data, _cancellable, _other):
        disk_usage = self.disk_info.get_disk_usage()
        data = {
            "icon": self.icon,
            "text": disk_usage.percentage,
            "storage": f"{disk_usage.used}/{disk_usage.total}",
            "used": self.disk_info.get_used_fraction(),
        }
        task.return_value(data)

    def _on_task_ready(self, task, _result, _user_data=None):
        try:
            task_dict = _result.propagate_value()[1]
            self.icon_label.set_label(task_dict.get("icon", "?"))
            self.text_label.set_label(task_dict.get("text", "Default text"))
            self.storage_label.set_label(task_dict.get("storage", "0B/0B"))
            self.used_bar.set_fraction(task_dict.get("used", "0B"))
        except Exception as e:
            print(e)
            pass
        finally:
            self._task_in_flight = False

    def populate_dropdown(self):
        self.dropdown.add(self.mountpoint_label)
        self.dropdown.add(self.used_bar)
        self.dropdown.add(self.storage_label)

    def on_click(self, user_data):
        self.dropdown.popup()
        return True
