from gi.repository import Gtk
from gi.repository import GLib

import re
import i3ipc

from ngb.modules import WidgetBox

class WorkspaceBox(WidgetBox):
    i3 = i3ipc.Connection()
    def __init__(self, name="", focused=False, urgent=False):
        self.name = name
        self.focused = focused
        super().__init__(text=self.name)
        self.icon_label.set_visible(False)
        self.set_focused()

    def set_focused(self):
        if(not self.focused):
            self.text_label.set_opacity(0.6)

    def on_click(self, sequence, user_data):
        if(self.name):
            self.i3.command(f"workspace {self.name}")

class Workspaces(Gtk.Box):
    workspaces = []
    i3 = i3ipc.Connection()
    def __init__(self, monitor="all"):
        super().__init__(spacing=5)
        self.monitor = monitor
        self.update_boxes()
        self.update_list()
        self.scroll_controller = Gtk.EventControllerScroll.new(Gtk.EventControllerScrollFlags.VERTICAL)
        self.scroll_controller.connect("scroll", self.on_scroll)
        self.add_controller(self.scroll_controller)

    def sort_key(self, item):
        name = item['name']
        # Use regex to separate numeric and non-numeric parts
        numeric_part = int(re.match(r'(\d+)', name).group(0)) if re.match(r'(\d+)', name) else float('inf')
        non_numeric_part = re.sub(r'^\d+', '', name)  # Remove numeric part for sorting
        return (numeric_part, non_numeric_part)

    def get_ws(self):
        ws_list = []
        workspaces = self.i3.get_workspaces()
        for ws in workspaces:
            ws_list.append({
                "name": ws.name,
                "focused": ws.focused,
                "output": ws.output,
                "urgent": ws.urgent
            })

        ws_list = sorted(ws_list, key=self.sort_key)
        self.workspaces = ws_list

    def update_boxes(self):
        self.get_ws()
        while self.get_first_accessible_child() is not None:
            self.remove(self.get_first_accessible_child())
        
        for ws in self.workspaces:
            if(self.monitor == "all" or ws["output"] == self.monitor):
                self.append(WorkspaceBox(name=ws["name"], focused=ws["focused"], urgent=ws["urgent"]))
        
        return True

    def update_list(self):
        GLib.timeout_add(100, self.update_boxes)

    def on_scroll(self, controller, x, y):
        if(y < 0):
            self.i3.command("workspace next_on_output")
        elif(y > 0):
            self.i3.command("workspace prev_on_output")