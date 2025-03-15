#!/usr/bin/env python3
from ctypes import CDLL
CDLL("libgtk4-layer-shell.so")

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Gtk4LayerShell", "1.0")
gi.require_version("Gdk", "4.0")

from gi.repository import Gtk

import sys

from ngb.widgets import Bluetooth, Clock, Cpu, Disk, Headset, Network, Volume, Weather, Workspaces
from ngb.modules import Bar, Config

class MainWindow(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="gtk.ngb")
        self.config = Config()

    def do_activate(self):
        for i in self.config.data['bars']:
            self.create_window(i)

    def create_window(self, bar_config):
        output = bar_config["output"]
        window = Bar(app=self, monitor=output)
        window.show()

        valid_widgets = {
            "bluetooth": Bluetooth,
            "clock": Clock,
            "cpu": Cpu,
            "disk": Disk,
            "headset": Headset,
            "network": Network,
            "volume": Volume,
            "weather": Weather,
            "workspace": Workspaces
        }

        for widget in bar_config["widgets"]["left"]:
            config = widget["config"]
            module = widget["module"]
            if(module in valid_widgets):
                window.left(valid_widgets.get(module)(**config))

        for widget in bar_config["widgets"]["center"]:
            config = widget["config"]
            module = widget["module"]
            if(module in valid_widgets):
                window.center(valid_widgets.get(module)(**config))

        for widget in bar_config["widgets"]["right"]:
            config = widget["config"]
            module = widget["module"]
            if(module in valid_widgets):
                window.right(valid_widgets.get(module)(**config))

def main():
    try:
        app = MainWindow()
        app.run(sys.argv)
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()