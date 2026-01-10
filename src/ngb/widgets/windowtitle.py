from gi.repository import Gtk
from gi.repository import GLib

import re
import os
from collections import namedtuple
import socket

from ngb.modules import HyprlandIpc, NiriIPC, SwayIPC, WidgetBox, WindowManagerIPC


class WindowTitle(WidgetBox):
    if os.environ["XDG_CURRENT_DESKTOP"] == "sway":
        wm = SwayIPC()
    elif os.environ["XDG_CURRENT_DESKTOP"] == "Hyprland":
        wm = HyprlandIpc()
    elif os.environ["XDG_CURRENT_DESKTOP"] == "niri":
        wm = NiriIPC()
    # If using a non-supported window manager and show empty space instead of giving error
    else:
        wm = WindowManagerIPC()

    def __init__(self, **kwargs):
        super().__init__(icon="")
        self.timer = kwargs.get("timer", 0.1)
        self.text = "Test"

    def run(self):
        self.get_window_title()
        self.update_window_title()

    def get_window_title(self):
        windows = self.wm.get_windows()
        for w in windows:
            if w.get("focused"):
                self.text = w.get("title")
                return True
        self.text = ""
        return True

    def update_window_title(self):
        GLib.timeout_add(self.timer * 1000, self.get_window_title)
