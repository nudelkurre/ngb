#!/usr/bin/env python3
from ctypes import CDLL
CDLL("libgtk4-layer-shell.so")

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Gtk4LayerShell", "1.0")
gi.require_version("Gdk", "4.0")

from gi.repository import Gtk
from gi.repository import Gtk4LayerShell as LayerShell
from gi.repository import Gdk
from gi.repository import GLib
from screeninfo import get_monitors

from pybar.widgets import Clock, Disk, Network
from pybar.modules import Bar

class MainWindow(Gtk.Application):
    monitors = {}
    active_monitor = ""
    
    def __init__(self, active_monitor, spacing=10):
        super().__init__(application_id="gtk.pybar")
        self.spacing = spacing
        self.active_monitor = active_monitor
        self.get_displays()
        self.connect("activate", self.on_activate)
        self.run(None)

    def get_displays(self):

        display = Gdk.Display.get_default()
        assert display is not None

        gdk_monitors = display.get_monitors()
        
        for m in get_monitors():
            self.monitors[m.name] = {}
            self.monitors[m.name]["width"] = m.width
            self.monitors[m.name]["height"] = m.height
            for gdkm in gdk_monitors:
                if(gdkm.get_connector() == m.name):
                    self.monitors[m.name]['monitor'] = gdkm

    def on_activate(self, app):
        window_width = self.monitors[self.active_monitor]["width"]
        window_height = self.monitors[self.active_monitor]["height"]
        window_monitor = self.monitors[self.active_monitor]["monitor"]
        window = Gtk.ApplicationWindow(application=app)
        window.set_default_size(window_width, 25)

        LayerShell.init_for_window(window)
        LayerShell.set_layer(window, LayerShell.Layer.BOTTOM)
        LayerShell.set_anchor(window, LayerShell.Edge.TOP, True)
        LayerShell.auto_exclusive_zone_enable(window)
        LayerShell.set_monitor(window, window_monitor)

        bar = Bar(spacing=self.spacing)
        disk = Disk("/")
        bar.right(disk)
        network = Network("eth0")
        bar.right(network)
        clocklabel = Clock("%Y-%m-%d %H:%M:%S")
        bar.right(clocklabel)
        window.set_child(bar)
        window.present()

def main():
    try:
        app = MainWindow("DP-1")
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()