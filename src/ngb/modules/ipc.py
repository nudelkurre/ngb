import os

from gi.repository import Gio, GLib, GObject

from .ipc_modules import MangoIPC, NiriIPC, SwayIPC, WindowManagerIPC
from ngb.utils import cut_string_length


class IPCModule(GObject.Object):
    valid_ipc = {"mango": MangoIPC, "niri": NiriIPC, "sway": SwayIPC}

    __gsignals__ = {
        "workspace-updates": (
            GObject.SignalFlags.RUN_LAST,
            None,
            (object,),
        ),
        "window-updates": (
            GObject.SignalFlags.RUN_LAST,
            None,
            (object,),
        ),
        "monitor-updates": (
            GObject.SignalFlags.RUN_LAST,
            None,
            (object,),
        ),
        "focused-window-updates": (
            GObject.SignalFlags.RUN_LAST,
            None,
            (object,),
        ),
        "keymode-updates": (
            GObject.SignalFlags.RUN_LAST,
            None,
            (object,),
        ),
    }

    def __init__(self, **kwargs):
        super().__init__()
        self.hide_no_focus = kwargs.get("hide_no_focus", False)
        self.title_max_length = kwargs.get("title_max_length", 200)
        self.current_wm = os.environ.get("XDG_CURRENT_DESKTOP", "").lower()
        self.timer = kwargs.get("timer")
        self.wm = self.valid_ipc.get(self.current_wm, WindowManagerIPC)(
            timer=self.timer
        )
        self.wm.connect("focused-window", self.on_focused_window)
        self.wm.connect("keymode", self.on_keymode_updates)
        self.wm.connect("monitors", self.on_monitor_updates)
        self.wm.connect("windows", self.on_window_updates)
        self.wm.connect("workspaces", self.on_workspace_updates)
        self.wm.start()

    def on_focused_window(self, instance, data):
        self.emit("focused-window-updates", data)

    def on_keymode_updates(self, instance, data):
        self.emit("keymode-updates", data)

    def on_window_updates(self, instance, data):
        self.emit("window-updates", data)

    def on_monitor_updates(self, instance, data):
        self.emit("monitor-updates", data)

    def on_workspace_updates(self, instance, data):
        self.emit("workspace-updates", data)

    def close_window(self, id):
        self.wm.close_window(id)

    def focus_window(self, id):
        self.wm.focus_window(id)

    def is_valid_wm(self):
        return (
            True
            if not isinstance(
                self.valid_ipc.get(self.current_wm, WindowManagerIPC), WindowManagerIPC
            )
            else False
        )

    def goto_workspace(self, name):
        if name and name != "":
            self.wm.command(f"workspace {name}")

    def next_workspace(self):
        self.wm.command("workspace next_on_output")

    def previous_workspace(self):
        self.wm.command("workspace prev_on_output")
