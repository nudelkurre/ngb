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
    def __init__(self, spacing=10):
        super().__init__(application_id="gtk.ngb")
        self.config = Config()

    def do_activate(self):
        for i in self.config.data['bars']:
            self.create_window(i)

    def create_window(self, bar_config):
        output = bar_config["output"]
        window = Bar(self, output)
        window.show()

        for widget in bar_config["widgets"]["left"]:
            config = widget["config"]
            match widget["module"]:
                case "bluetooth":
                    window.left(Bluetooth())
                case "clock":
                    window.left(Clock(timeformat_normal=config["format"], timeformat_hover=config["format_hover"]))
                case "cpu":
                    window.left(Cpu())
                case "disk":
                    window.left(Disk(mountpoint=config["mountpoint"]))
                case "headset":
                    window.left(Headset())
                case "network":
                    window.left(Network(interface=config["interface"]))
                case "volume":
                    window.left(Volume())
                case "weather":
                    window.left(Weather(city=config["city"]))
                case "workspace":
                    window.left(Workspaces(monitor=widget["config"]["monitor"], ws_names=widget["config"]["names"]))

        for widget in bar_config["widgets"]["center"]:
            config = widget["config"]
            match widget["module"]:
                case "bluetooth":
                    window.center(Bluetooth())
                case "clock":
                    window.center(Clock(timeformat_normal=config["format"], timeformat_hover=config["format_hover"]))
                case "cpu":
                    window.center(Cpu())
                case "disk":
                    window.center(Disk(mountpoint=config["mountpoint"]))
                case "headset":
                    window.center(Headset())
                case "network":
                    window.center(Network(interface=config["interface"]))
                case "volume":
                    window.center(Volume())
                case "weather":
                    window.center(Weather(city=config["city"]))
                case "workspace":
                    window.center(Workspaces(monitor=widget["config"]["monitor"]))

        for widget in bar_config["widgets"]["right"]:
            config = widget["config"]
            match widget["module"]:
                case "bluetooth":
                    window.right(Bluetooth())
                case "clock":
                    window.right(Clock(timeformat_normal=config["format"], timeformat_hover=config["format_hover"]))
                case "cpu":
                    window.right(Cpu())
                case "disk":
                    window.right(Disk(mountpoint=config["mountpoint"]))
                case "headset":
                    window.right(Headset())
                case "network":
                    window.right(Network(interface=config["interface"]))
                case "volume":
                    window.right(Volume())
                case "weather":
                    window.right(Weather(city=config["city"]))
                case "workspace":
                    window.right(Workspaces(monitor=widget["config"]["monitor"]))

def main():
    try:
        app = MainWindow()
        app.run(sys.argv)
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()