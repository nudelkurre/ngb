from gi.repository import Gtk
from gi.repository import GLib
from gi.repository import Gdk

class WidgetBox(Gtk.Box):
    def __init__(self, icon="", icon_size=20, text="", timer=1000, spacing=10):
        super().__init__(spacing=spacing)
        self.timer = timer
        self.text = text
        self.icon = icon
        self.icon_size = icon_size
        self.icon_label = Gtk.Label()
        self.text_label = Gtk.Label()
        self.scroll_controller = Gtk.EventControllerScroll.new(Gtk.EventControllerScrollFlags.VERTICAL)
        self.scroll_controller.connect("scroll", self.on_scroll)
        self.add_controller(self.scroll_controller)
        self.hover_controller = Gtk.EventControllerMotion.new()
        self.hover_controller.connect("enter", self.on_hover_enter)
        self.hover_controller.connect("leave", self.on_hover_leave)
        self.add_controller(self.hover_controller)
        self.click_controller = Gtk.GestureClick.new()
        self.click_controller.connect("pressed", self.on_click)
        self.add_controller(self.click_controller)
        self.append(self.icon_label)
        self.append(self.text_label)
        self.set_icon()
        self.set_text()
        self.update_label()

    def on_scroll(self, controller, x, y):
        pass

    def on_hover_enter(self, controller, x, y):
        pass

    def on_hover_leave(self, controller):
        pass

    def on_click(self, controller, n_press, x, y):
        pass

    def set_icon(self):
        self.icon_label.set_markup(f"<span size=\"{self.icon_size * 1000}\">{self.icon}</span>")
        return True

    def set_text(self):
        self.text_label.set_label(self.text)
        return True

    def update_label(self):
        GLib.timeout_add(self.timer, self.set_text)
        return True