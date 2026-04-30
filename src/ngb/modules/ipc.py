import os

from .niriipc import NiriIPC
from .swayipc import SwayIPC
from .windowmanageripc import WindowManagerIPC


class IPCModule:
    valid_ipc = {"niri": NiriIPC, "sway": SwayIPC}

    def __init__(self, **kwargs):
        self.hide_no_focus = kwargs.get("hide_no_focus", False)
        self.title_max_length = kwargs.get("title_max_length", 200)
        self.current_wm = os.environ.get("XDG_CURRENT_DESKTOP").lower()
        self.wm = self.valid_ipc.get(self.current_wm)()

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

    def get_windows(self):
        return self.wm.get_windows()

    def get_window_title(self):
        window = self.wm.get_focused_window()
        if window == "":
            if not self.hide_no_focus:
                return "Empty"
            return ""
        return self.cut_title_lenght(window)

    def get_workspaces(self):
        ws_list = []
        workspaces = self.wm.get_workspaces()
        ws_list = sorted(workspaces, key=lambda d: int(d.id))
        return ws_list

    def goto_workspace(self, name):
        if name and name != "":
            self.wm.command(f"workspace {name}")

    def next_workspace(self):
        self.wm.command("workspace next_on_output")

    def previous_workspace(self):
        self.wm.command("workspace prev_on_output")

    def cut_title_lenght(self, title):
        old_title = title.split(" ")
        new_title = title[: self.title_max_length].split(" ")
        new_title_last_index = len(new_title) - 1
        if old_title[new_title_last_index] == new_title[new_title_last_index]:
            return " ".join(new_title)
        else:
            return " ".join(new_title[:-1])
