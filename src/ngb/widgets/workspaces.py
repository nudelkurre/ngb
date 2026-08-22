from gi.repository import Gtk
from gi.repository import GLib

from ngb.modules import IPCModule, WidgetBox, WidgetDrawer


class WorkspaceBox(WidgetBox):

    def __init__(self, **kwargs):
        self.name = kwargs.get("name", "")
        self.show_name = kwargs.get("show_name", "")
        self.focused = kwargs.get("focused", False)
        self.urgent = kwargs.get("urgent", False)
        self.icon_size = kwargs.get("icon_size", 20)
        self.wm = kwargs.get("wm")
        super().__init__(icon=self.show_name, text=self.name, icon_size=self.icon_size)
        if self.urgent:
            self.add_css_class("urgent-workspace")
        self.set_focused()

    def set_focused(self):
        if not self.focused and not self.urgent:
            self.icon_label.set_opacity(0.6)
            self.text_label.set_opacity(0.6)

    def _task_func(self, task, _task_data, _cancellable, _other):
        if self.show_name != "" or True:
            data = {"icon": self.icon}
        else:
            data = {"text": self.text}
        task.return_value(data)

    def on_click(self, user_data):
        if self.wm:
            self.wm.goto_workspace(self.name)


class Workspaces(WidgetDrawer):
    def __init__(self, **kwargs):
        self.spacing = kwargs.get("spacing", 5)
        self.icon_size = kwargs.get("icon_size", 20)
        self.wm_api = IPCModule(**kwargs)
        self.timer = kwargs.get("timer", 0.1)
        self.monitor = kwargs.get("monitor", "all")
        self.use_workspace_names = kwargs.get("use_workspace_names", False)
        self.ws_names = kwargs.get("names", {})
        self.default_name = kwargs.get("default_name", "*")
        super().__init__(spacing=self.spacing, timer=self.timer)

    def on_scroll(self, controller, x, y):
        if self.wm_api:
            if y < 0:
                self.wm_api.next_workspace()
            elif y > 0:
                self.wm_api.previous_workspace()

    def get_boxes(self):
        return self.wm_api.get_workspaces()

    def create_widget(self, box):
        if self.monitor == "all" or box.output == self.monitor:
            if self.use_workspace_names:
                show_name = box.name
            else:
                if box.name in self.ws_names:
                    show_name = self.ws_names.get(box.name, {})
                else:
                    show_name = self.default_name
            return WorkspaceBox(
                id=box.id,
                name=box.name,
                show_name=show_name,
                focused=box.focused,
                urgent=box.urgent,
                wm=self.wm_api,
            )
        else:
            return None
