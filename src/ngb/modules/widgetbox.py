from gi.repository import Gtk
from gi.repository import GLib

class WidgetBox(Gtk.Box):
    def __init__(self, icon="", icon_size=20, text="", timer=1000, spacing=10):
        self.spacing = spacing
        self.timer = timer
        self.text = text
        self.icon = icon
        self.icon_size = icon_size
        Gtk.Box.__init__(self, spacing=self.spacing)
        self.append(self.icon_label)
        self.append(self.text_label)
        self.set_icon()
        self.set_text()
        self.update_label()

    def set_icon(self):
        self.icon_label.set_markup(f"<span size=\"{self.icon_size * 1000}\">{self.icon}</span>")
        return True

    def set_text(self):
        self.text_label.set_label(self.text)
        return True

    def update_label(self):
        GLib.timeout_add(self.timer, self.set_text)
        return True