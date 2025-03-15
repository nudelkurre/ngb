from gi.repository import Gtk
from gi.repository import Gtk4LayerShell as LayerShell
from gi.repository import Gdk
from gi.repository import GLib
from screeninfo import get_monitors

class Bar(Gtk.ApplicationWindow):
    monitors = {}
    active_monitor = ""
    def __init__(self, **kwargs):
        self.app = kwargs.get("app")
        self.monitor = kwargs.get("monitor")
        super().__init__(application=self.app)

        self.get_displays()
        self.active_monitor = self.monitor

        window_width = self.monitors[self.active_monitor]["width"]
        window_height = self.monitors[self.active_monitor]["height"]
        window_monitor = self.monitors[self.active_monitor]["monitor"]
        self.set_default_size(window_width, 25)

        LayerShell.init_for_window(self)
        LayerShell.set_layer(self, LayerShell.Layer.BOTTOM)
        LayerShell.set_anchor(self, LayerShell.Edge.TOP, True)
        LayerShell.auto_exclusive_zone_enable(self)
        LayerShell.set_monitor(self, window_monitor)

        bar = Gtk.CenterBox()

        self.set_child(bar)
        self.present()

        self.leftbox = Gtk.Box()
        self.centerbox = Gtk.Box()
        self.rightbox = Gtk.Box()

        bar.set_start_widget(self.leftbox)
        bar.set_center_widget(self.centerbox)
        bar.set_end_widget(self.rightbox)
        
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

    def on_destroy(self, event):
        self.destroy()

    def left(self, widget):
        self.leftbox.append(widget)
        return True

    def center(self, widget):
        self.centerbox.append(widget)
        return True

    def right(self, widget):
        self.rightbox.append(widget)
        return True