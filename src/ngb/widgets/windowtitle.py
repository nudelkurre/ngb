from gi.repository import Gtk
from gi.repository import GLib

import re
import os
from collections import namedtuple
import socket

from ngb.modules import HyprlandIpc, NiriIPC, SwayIPC, WidgetBox, WindowManagerIPC


class WindowButton(Gtk.Box):
    def __init__(self, **kwargs):
        super().__init__()
        self.window = kwargs.get("window", {})
        self.wm = kwargs.get("wm")
        self.dropdown = kwargs.get("dropdown")
        self.window_title = self.window.get("title", "")
        self.window_id = self.window.get("id")
        self.window_button = Gtk.Button(label=self.window_title)
        self.window_button.add_css_class("widget-button")
        self.window_button.connect("clicked", self.focus_window)
        self.append(self.window_button)

    def focus_window(self, user_data):
        self.wm.focus_window(self.window_id)
        self.dropdown.popdown()


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
        super().__init__(icon="", spacing=1)
        self.timer = kwargs.get("timer", 0.1)
        self.hide_no_focus = kwargs.get("hide_no_focus", False)
        self.text = "Test"

    def run(self):
        self.update_label()
        self.dropdown.connect("closed", self.on_close)
        self.get_window_title()
        self.update_window_title()

    def populate_dropdown(self):
        window_list = self.get_windows()
        for window in window_list:
            self.dropdown.add(
                WindowButton(window=window, wm=self.wm, dropdown=self.dropdown)
            )

    def get_windows(self):
        windows = self.wm.get_windows()
        return windows

    def get_window_title(self):
        window = self.wm.get_focused_window()
        if window == "":
            if self.hide_no_focus:
                self.set_visible(False)
            else:
                window = "No window in focus"
        else:
            if not self.get_visible():
                self.set_visible(True)
        self.text = window
        return True

    def on_click(self, user_data):
        if not isinstance(self.wm, HyprlandIpc):
            self.populate_dropdown()
            self.dropdown.popup()
        return True

    def on_close(self, user_data):
        self.dropdown.clear()
        return True

    def update_window_title(self):
        GLib.timeout_add(self.timer * 1000, self.get_window_title)
