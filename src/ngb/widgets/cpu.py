from gi.repository import Gtk
from gi.repository import GLib
import psutil
from psutil._common import bytes2human

from ngb.modules import WidgetBox


class Cpu(WidgetBox):
    def __init__(self, **kwargs):
        self.timer = kwargs.get("timer", 2)
        self.icon = kwargs.get("icon", "")
        self.icon_size = kwargs.get("icon_size", 20)
        super().__init__(timer=self.timer, icon=self.icon, icon_size=self.icon_size)

    def _task_func(self, task, _task_data, _cancellable, _other):
        usage = psutil.cpu_percent()
        data = {"text": f"{usage}%", "icon": self.icon}
        task.return_value(data)
