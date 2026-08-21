from gi.repository import Gtk
from gi.repository import GLib

from ngb.modules import BluetoothModule, WidgetBox, WidgetDrawer


class BluetoothBox(WidgetBox):
    def __init__(self, **kwargs):
        self.text = kwargs.get("text", "")
        self.icon = kwargs.get("icon", "?")
        self.name = kwargs.get("name", "")
        self.timer = kwargs.get("timer", 5)
        self.spacing = kwargs.get("spacing", 10)
        self.icon_size = kwargs.get("icon_size", 20)
        super().__init__(
            icon=self.icon,
            text=self.text,
            timer=self.timer,
            spacing=self.spacing,
            icon_size=self.icon_size,
        )

    def _task_func(self, task, _task_data, _cancellable, _other):
        data = {"text": self.text, "icon": self.icon, "tooltip": self.name}
        task.return_value(data)


class Bluetooth(WidgetDrawer):

    def __init__(self, **kwargs):
        self.timer = kwargs.get("timer", 5)
        self.spacing = kwargs.get("spacing", 10)
        self.icon_size = kwargs.get("icon_size", 20)
        self.devices = BluetoothModule()
        super().__init__(spacing=self.spacing, timer=self.timer)
        self.is_stopped = False
        self.timeout = None

    def get_boxes(self):
        return self.devices.get_device_list()

    def create_widget(self, box):
        return BluetoothBox(
            icon=box.icon, text=box.battery, connected=box.connected, name=box.name
        )
