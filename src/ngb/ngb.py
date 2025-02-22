#!/usr/bin/env python3
from ctypes import CDLL
CDLL("libgtk4-layer-shell.so")

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Gtk4LayerShell", "1.0")
gi.require_version("Gdk", "4.0")

from gi.repository import Gtk

import sys

from ngb.widgets import Clock, Disk, Network, Volume
from ngb.modules import Bar

class MainWindow(Gtk.Application):
    def __init__(self, spacing=10):
        super().__init__(application_id="gtk.ngb")

    def do_activate(self):
        for i in ["DP-1", "HDMI-A-1"]:
            self.create_window(i)

    def create_window(self, monitor):
        window = Bar(self, monitor)
        window.show()
        
        """
        Widgets added just to test until config file implemented
        to create bars with widgets dynamicly
        """
        window.center(Gtk.Label(label=monitor))
        window.right(Disk("/"))
        window.right(Network("eth0"))
        window.right(Volume())
        window.right(Clock())

def main():
    try:
        app = MainWindow()
        app.run(sys.argv)
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()