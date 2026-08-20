from gi.repository import Gtk
from gi.repository import GLib

from ngb.modules import HeadsetModule, WidgetBox


class Headset(WidgetBox):
    min_timer = 5

    def __init__(self, **kwargs):
        self.default_icon = "󰋎"
        self.warning_icon = ""
        self.icon = kwargs.get("icon", self.default_icon)
        self.timer = kwargs.get("timer", self.min_timer)
        if self.timer < self.min_timer:
            self.timer = self.min_timer
        self.icon_size = kwargs.get("icon_size", 20)
        self.headset = HeadsetModule()
        super().__init__(icon=self.icon, icon_size=self.icon_size, timer=self.timer)

    def _task_func(self, task, _task_data, _cancellable, _other):
        battery_levels = self.headset.get_headset_info()
        if isinstance(battery_levels, list) and len(battery_levels) > 0:
            data = {"text": " ".join(battery_levels), "icon": self.default_icon}
            task.return_value(data)
        elif battery_levels == -1:
            data = {"text": "", "error": -1, "tooltip": "Process timed out"}
            task.return_value(data)
        elif battery_levels == -2:
            data = {
                "text": "",
                "icon": self.warning_icon,
                "tooltip": "headsetcontrol not installed",
                "error": -2,
            }
            task.return_value(data)
        else:
            data = {}
            task.return_value(data)

    def _on_task_ready(self, task, _result, _user_data=None):
        try:
            task_dict = _result.propagate_value()[1]
            if task_dict != {}:
                self.set_visible(True)
                self.text_label.set_text(task_dict.get("text", "Default text"))
                self.icon_label.set_text(task_dict.get("icon", "?"))
                self.set_tooltip_text(task_dict.get("tooltip", ""))
                if task_dict.get("error") == -1:
                    self.stop()
            else:
                self.set_visible(False)
        except Exception as e:
            pass
        finally:
            self._task_in_flight = False
