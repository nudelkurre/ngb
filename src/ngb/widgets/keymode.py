from gi.repository import Gtk
from gi.repository import GLib

from ngb.modules import IPCModule, WidgetBox


class KeyMode(WidgetBox):
    def __init__(self, **kwargs):
        super().__init__(icon="", spacing=1)
        self.icons = kwargs.get("keymode_icons", {})
        self.wm_api = IPCModule()
        self.wm_api.connect("keymode-updates", self.on_keymode_updates)
        self.keymode = ""

    def on_keymode_updates(self, instance, data):
        self.keymode = self.icons.get(data, data)
        self.update_label()

    def _task_func(self, task, _task_data, _cancellable, _other):
        data = {"text": self.keymode}
        task.return_value(data)
