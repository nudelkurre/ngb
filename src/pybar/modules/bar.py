from gi.repository import Gtk
from gi.repository import GLib

class Bar(Gtk.CenterBox):
    def __init__(self, spacing=6):
        Gtk.CenterBox.__init__(self)
        self.leftbox = Gtk.Box(spacing=spacing)
        self.centerbox = Gtk.Box(spacing=spacing)
        self.rightbox = Gtk.Box(spacing=spacing)
        self.set_start_widget(self.leftbox)
        self.set_center_widget(self.centerbox)
        self.set_end_widget(self.rightbox)

    def left(self, widget):
        self.leftbox.append(widget)
        return True

    def center(self, widget):
        self.centerbox.append(widget)
        return True

    def right(self, widget):
        self.rightbox.append(widget)
        return True