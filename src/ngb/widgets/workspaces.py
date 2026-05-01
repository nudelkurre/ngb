from gi.repository import Gtk
from gi.repository import GLib

from ngb.modules import IPCModule, WidgetBox


class WorkspaceBox(WidgetBox):

    def __init__(self, **kwargs):
        self.name = kwargs.get("name", "")
        self.show_name = kwargs.get("show_name", "")
        self.focused = kwargs.get("focused", False)
        self.urgent = kwargs.get("urgent", False)
        self.icon_size = kwargs.get("icon_size", 20)
        self.wm = kwargs.get("wm")
        super().__init__(icon=self.show_name, text=self.name, icon_size=self.icon_size)
        self.hide_label()
        self.set_focused()
        self.set_icon()

    def set_focused(self):
        if not self.focused:
            self.icon_label.set_opacity(0.6)
            self.text_label.set_opacity(0.6)

    def hide_label(self):
        if self.show_name != "":
            self.icon_label.set_visible(True)
            self.text_label.set_visible(False)
        else:
            self.icon_label.set_visible(False)
            self.text_label.set_visible(True)

    def on_click(self, user_data):
        self.wm.goto_workspace(self.name)


class Workspaces(Gtk.Box):
    workspaces = []
    old_workspaces = []

    def __init__(self, **kwargs):
        pass
        self.spacing = kwargs.get("spacing", 5)
        self.icon_size = kwargs.get("icon_size", 20)
        super().__init__(spacing=self.spacing)
        self.wm_api = IPCModule(**kwargs)
        self.timer = kwargs.get("timer", 0.1)
        self.monitor = kwargs.get("monitor", "all")
        self.use_workspace_names = kwargs.get("use_workspace_names", False)
        self.ws_names = kwargs.get("names", {})
        self.default_name = kwargs.get("default_name", "*")
        self.is_stopped = False
        self.timeout = None
        self.update_boxes()
        self.update_list()
        self.scroll_controller = Gtk.EventControllerScroll.new(
            Gtk.EventControllerScrollFlags.VERTICAL
        )
        self.scroll_controller.connect("scroll", self.on_scroll)
        self.add_controller(self.scroll_controller)

    def run(self):
        pass

    def stop(self):
        self.is_stopped = True
        if self.timeout:
            GLib.source_remove(self.timeout)
            self.timeout = None

    def remove_widget(self):
        parent = self.get_parent()
        if parent:
            parent.remove(self)

    def update_boxes(self):
        self.workspaces = self.wm_api.get_workspaces()
        if self.workspaces != self.old_workspaces:
            self.old_workspaces = self.workspaces
            while self.get_first_accessible_child() is not None:
                self.remove(self.get_first_accessible_child())

            for ws in self.workspaces:
                if self.monitor == "all" or ws.output == self.monitor:
                    if self.use_workspace_names:
                        show_name = ws.name
                    else:
                        if ws.name in self.ws_names:
                            show_name = self.ws_names.get(ws.name, {})
                        else:
                            show_name = self.default_name
                    self.append(
                        WorkspaceBox(
                            id=ws.id,
                            name=ws.name,
                            show_name=show_name,
                            focused=ws.focused,
                            urgent=ws.urgent,
                            icon_size=self.icon_size,
                            wm=self.wm_api,
                        )
                    )
        return True

    def update_list(self):
        self.timeout = GLib.timeout_add(self.timer * 1000, self.update_boxes)

    def on_scroll(self, controller, x, y):
        if y < 0:
            self.wm_api.next_workspace()
        elif y > 0:
            self.wm_api.previous_workspace()
