from gi.repository import Gtk
from gi.repository import GLib

import re
import os
from collections import namedtuple
import socket

from ngb.modules import HyprlandIpc, NiriIPC, SwayIPC, WidgetBox, WindowManagerIPC

class WorkspaceBox(WidgetBox):
    if(os.environ["XDG_CURRENT_DESKTOP"] == "sway"):
        wm = SwayIPC()
    elif(os.environ["XDG_CURRENT_DESKTOP"] == "Hyprland"):
        wm = HyprlandIpc()
    elif(os.environ["XDG_CURRENT_DESKTOP"] == "niri"):
        wm = NiriIPC()
    # If using a non-supported window manager and show empty space instead of giving error
    else:
        wm = WindowManagerIPC()
    def __init__(self, **kwargs):
        self.name = kwargs.get("name", "")
        self.show_name = kwargs.get("show_name", "")
        self.focused = kwargs.get("focused", False)
        self.urgent = kwargs.get("urgent", False)
        self.icon_size = kwargs.get("icon_size", 20)
        super().__init__(icon=self.show_name, text=self.name, icon_size=self.icon_size)
        self.hide_label()
        self.set_focused()

    def set_focused(self):
        if(not self.focused):
            self.icon_label.set_opacity(0.6)
            self.text_label.set_opacity(0.6)

    def hide_label(self):
        if(self.show_name != ""):
            self.icon_label.set_visible(True)
            self.text_label.set_visible(False)
        else:
            self.icon_label.set_visible(False)
            self.text_label.set_visible(True)

    def on_click(self, user_data):
        if(self.name):
            self.wm.command(f"workspace {self.name}")

class Workspaces(Gtk.Box):
    workspaces = []
    old_workspaces = []
    if(os.environ["XDG_CURRENT_DESKTOP"] == "sway"):
        wm = SwayIPC()
    elif(os.environ["XDG_CURRENT_DESKTOP"] == "Hyprland"):
        wm = HyprlandIpc()
    elif(os.environ["XDG_CURRENT_DESKTOP"] == "niri"):
        wm = NiriIPC()
    # If using a non-supported window manager and show empty space instead of giving error
    else:
        wm = WindowManagerIPC()
    def __init__(self, **kwargs):
        self.spacing = kwargs.get("spacing", 5)
        self.icon_size = kwargs.get("icon_size", 20)
        super().__init__(spacing=self.spacing)
        self.timer = kwargs.get("timer", 0.1)
        self.monitor = kwargs.get("monitor", "all")
        self.ws_names = kwargs.get("names", {})
        self.update_boxes()
        self.update_list()
        self.scroll_controller = Gtk.EventControllerScroll.new(Gtk.EventControllerScrollFlags.VERTICAL)
        self.scroll_controller.connect("scroll", self.on_scroll)
        self.add_controller(self.scroll_controller)

    def get_ws(self):
        ws_list = []
        workspaces = self.wm.get_workspaces()
        for ws in workspaces:
            ws_list.append({
                "id": ws.id,
                "name": ws.name,
                "focused": ws.focused,
                "output": ws.output,
                "urgent": ws.urgent
            })

        ws_list = sorted(ws_list, key=lambda d: int(d["id"]))
        self.workspaces = ws_list

    def update_boxes(self):
        self.get_ws()
        if(self.workspaces != self.old_workspaces):
            self.old_workspaces = self.workspaces
            while self.get_first_accessible_child() is not None:
                self.remove(self.get_first_accessible_child())
            
            for ws in self.workspaces:
                if(self.monitor == "all" or ws["output"] == self.monitor):
                    show_name = self.ws_names[ws["name"]] if ws["name"] in self.ws_names else ""
                    if(ws["name"]):
                        self.append(WorkspaceBox(id=ws["id"], name=ws["name"], show_name=show_name, focused=ws["focused"], urgent=ws["urgent"], icon_size=self.icon_size))
        
        return True

    def update_list(self):
        GLib.timeout_add(self.timer * 1000, self.update_boxes)

    def on_scroll(self, controller, x, y):
        if(y < 0):
            self.wm.command("workspace next_on_output")
        elif(y > 0):
            self.wm.command("workspace prev_on_output")