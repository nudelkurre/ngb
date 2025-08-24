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
        self.location = kwargs.get("location", "top").lower()
        self.gaps = kwargs.get("gaps", 0)
        self.layer = kwargs.get("layer", "bottom").lower()
        super().__init__(application=self.app)

        self.get_displays()
        self.active_monitor = self.monitor

        window_width = self.monitors[self.active_monitor]["width"]
        window_height = self.monitors[self.active_monitor]["height"]
        window_monitor = self.monitors[self.active_monitor]["monitor"]
        self.set_default_size(window_width - (self.gaps * 2), 25)

        LayerShell.init_for_window(self)
        if(self.layer == "top"):
            LayerShell.set_layer(self, LayerShell.Layer.TOP)
        elif(self.layer == "overlay"):
            LayerShell.set_layer(self, LayerShell.Layer.OVERLAY)
        elif(self.layer == "background"):
            LayerShell.set_layer(self, LayerShell.Layer.BACKGROUND)
        else:
            LayerShell.set_layer(self, LayerShell.Layer.BOTTOM)
        if(self.location == "bottom"):
            LayerShell.set_anchor(self, LayerShell.Edge.BOTTOM, True)
        else:
            LayerShell.set_anchor(self, LayerShell.Edge.TOP, True)
        LayerShell.auto_exclusive_zone_enable(self)
        LayerShell.set_monitor(self, window_monitor)
        LayerShell.set_margin(self, LayerShell.Edge.TOP, self.gaps)
        LayerShell.set_margin(self, LayerShell.Edge.BOTTOM, self.gaps)
        LayerShell.set_margin(self, LayerShell.Edge.LEFT, self.gaps)
        LayerShell.set_margin(self, LayerShell.Edge.RIGHT, self.gaps)
        LayerShell.set_namespace(self, "ngb")

        bar = Gtk.CenterBox()

        self.set_child(bar)
        self.present()

        self.leftbox = Gtk.Box()
        self.leftbox.add_css_class("widget-box")
        self.centerbox = Gtk.Box()
        self.centerbox.add_css_class("widget-box")
        self.rightbox = Gtk.Box()
        self.rightbox.add_css_class("widget-box")

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