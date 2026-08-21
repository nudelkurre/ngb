from gi.repository import Gtk
from gi.repository import GLib

from ngb.modules import HeadsetModule, WidgetBox, WidgetDrawer


class HeadsetBox(WidgetBox):
    def __init__(self, **kwargs):
        self.device = kwargs.get("device")
        self.text = f"{self.device.batterylevel}%"
        self.icon = self.device.icon
        self.icon_size = kwargs.get("icon_size", 20)
        self.timer = kwargs.get("timer")
        super().__init__(
            text=self.text, icon=self.icon, icon_size=self.icon_size, timer=self.timer
        )
        self.name = self.device.name
        self.batterylevel = self.device.batterylevel

    def _task_func(self, task, _task_data, _cancellable, _other):
        if self.device.error is None:
            if self.batterylevel > 0:
                data = {"text": self.text, "icon": self.icon, "tooltip": self.name}
            else:
                data = {}
        else:
            if self.device.error == -1:
                data = {"icon": self.icon, "tooltip": "Process timed out"}
            elif self.device.error == -2:
                data = {"icon": self.icon, "tooltip": "headsetcontrol is not installed"}
            else:
                data = {}
        task.return_value(data)


class Headset(WidgetDrawer):
    min_timer = 5

    def __init__(self, **kwargs):
        self.timer = kwargs.get("timer", self.min_timer)
        if self.timer < self.min_timer:
            self.timer = self.min_timer
        self.spacing = kwargs.get("spacing", 10)
        self.icon_size = kwargs.get("icon_size", 20)
        self.headset = HeadsetModule()
        super().__init__(spacing=self.spacing, timer=self.timer)
        self.is_stopped = False
        self.timeout = None

    def get_boxes(self):
        return self.headset.get_headset_info()

    def create_widget(self, box):
        return HeadsetBox(device=box, icon_size=self.icon_size, timer=self.timer)
