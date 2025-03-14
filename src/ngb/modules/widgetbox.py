from gi.repository import Gtk
from gi.repository import GLib
from gi.repository import Gdk
from gi.repository import Gio

class WidgetBox(Gtk.Box):
    icon_size = 0
    def __init__(self, **kwargs):
        self.spacing = kwargs.get("spacing", 10)
        self.timer = kwargs.get("timer", 1)
        self.text = kwargs.get("text", "")
        self.icon = kwargs.get("icon", "")
        super().__init__(spacing=self.spacing)
        self.icon_label = Gtk.Label()
        self.text_label = Gtk.Label()
        self.scroll_controller = Gtk.EventControllerScroll.new(Gtk.EventControllerScrollFlags.VERTICAL)
        self.scroll_controller.connect("scroll", self.on_scroll)
        self.add_controller(self.scroll_controller)
        self.hover_controller = Gtk.EventControllerMotion.new()
        self.hover_controller.connect("enter", self.on_hover_enter)
        self.hover_controller.connect("leave", self.on_hover_leave)
        self.add_controller(self.hover_controller)
        self.click_controller = Gtk.GestureSingle()
        self.click_controller.set_button(1)
        self.click_controller.connect("begin", self.on_click)
        self.add_controller(self.click_controller)
        self.middle_click_controller = Gtk.GestureSingle()
        self.middle_click_controller.set_button(2)
        self.middle_click_controller.connect("begin", self.on_middle_click)
        self.add_controller(self.middle_click_controller)
        self.right_click_controller = Gtk.GestureSingle()
        self.right_click_controller.set_button(3)
        self.right_click_controller.connect("begin", self.on_right_click)
        self.add_controller(self.right_click_controller)
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

    def on_click(self, sequence, user_data):
        pass

    def on_middle_click(self, sequence, user_data):
        pass

    def on_right_click(self, sequence, user_data):
        pass

    def get_font_size_from_gsettings(self):
        settings = Gio.Settings.new('org.gnome.desktop.interface')
        font_name = settings.get_string('font-name')
        font_size = None
        for part in reversed(font_name.split()):
            if part.isdigit():
                font_size = int(part)
                break
        return font_size

    def set_icon(self):
        self.icon_size = self.get_font_size_from_gsettings() * 2
        self.icon_label.set_markup(f"<span size=\"{self.icon_size * 1000}\">{self.icon}</span>")
        return True

    def set_text(self):
        self.text_label.set_label(self.text)
        return True

    def update_label(self):
        GLib.timeout_add(self.timer * 1000, self.set_text)
        return True