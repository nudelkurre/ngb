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

class MainWindow(Gtk.Application):
    monitors = {}
    active_monitor = ""
    
    def __init__(self, active_monitor):
        Gtk.Application.__init__(self, application_id="gtk.pybar")
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

        box = Gtk.CenterBox()
        leftbox = Gtk.Box(spacing=6)
        centerbox = Gtk.Box(spacing=6)
        rightbox = Gtk.Box(spacing=6)
        box.set_start_widget(leftbox)
        box.set_center_widget(centerbox)
        box.set_end_widget(rightbox)
        leftlabel = Gtk.Label(label="Left")
        centerlabel = Gtk.Label(label="Center")
        rightlabel = Gtk.Label(label="Right")
        leftbox.append(leftlabel)
        centerbox.append(centerlabel)
        rightbox.append(rightlabel)
        disk = Disk("/")
        rightbox.append(disk)
        network = Network("eth0")
        rightbox.append(network)
        clocklabel = Clock("%Y-%m-%d %H:%M:%S")
        rightbox.append(clocklabel)
        window.set_child(box)
        window.present()

def main():
    try:
        app = MainWindow("DP-1")
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()