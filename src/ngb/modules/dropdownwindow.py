from gi.repository import Gtk
from gi.repository import GLib
from gi.repository import Gdk
from gi.repository import Gio


class DropDownWindow(Gtk.Popover):
    def __init__(self, **kwargs):
        super().__init__()
        self.spacing = kwargs.get("spacing", 6)
        self.orientation = kwargs.get("orientation", "vertical")
        self.box = Gtk.Box(spacing=self.spacing, orientation=self.orientation)
        self.box.add_css_class("dropdown")
        self.set_child(self.box)
        self.box.set_margin_start(self.spacing * 3)
        self.box.set_margin_end(self.spacing * 3)
        self.set_has_arrow(False)

    def add(self, widget):
        self.box.append(widget)
        return True

    def remove(self, widget):
        self.box.remove(widget)
        return True

    def clear(self):
        while self.box.get_first_child() is not None:
            self.box.remove(self.box.get_first_child())
        return True
