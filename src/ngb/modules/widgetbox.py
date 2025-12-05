from gi.repository import Gtk
from gi.repository import GLib
from gi.repository import Gdk
from gi.repository import Gio

from ngb.modules import DropDownWindow


class WidgetBox(Gtk.Button):
    # icon_size = 0

    def __init__(self, **kwargs):
        self.spacing = kwargs.get("spacing", 10)
        self.timer = kwargs.get("timer", 1)
        self.text = kwargs.get("text", "")
        self.icon = kwargs.get("icon", "")
        self.icon_size = kwargs.get("icon_size", 20)
        super().__init__()

        # Set css class to use the custom css created
        self.add_css_class("widget-button")

        # Create labels for icon and text for button
        self.icon_label = Gtk.Label()
        self.text_label = Gtk.Label()

        # Create a box to add multiple items to button
        self.box = Gtk.Box(spacing=self.spacing)
        self.set_child(self.box)

        # Create a dropdown window
        self.dropdown = DropDownWindow(orientation="vertical", spacing=self.spacing)
        self.append(self.dropdown)

        # Create a controller for scroll events
        self.scroll_controller = Gtk.EventControllerScroll.new(
            Gtk.EventControllerScrollFlags.VERTICAL
        )
        self.scroll_controller.connect("scroll", self.on_scroll)
        self.box.add_controller(self.scroll_controller)

        # Create a controller for hover events
        self.hover_controller = Gtk.EventControllerMotion.new()
        self.hover_controller.connect("enter", self.on_hover_enter)
        self.hover_controller.connect("leave", self.on_hover_leave)
        self.box.add_controller(self.hover_controller)

        # Create a controller for click events events
        # left click
        self.connect("clicked", self.on_click)
        # middle click
        self.middle_click_controller = Gtk.GestureSingle()
        self.middle_click_controller.set_button(2)
        self.middle_click_controller.connect("begin", self.on_middle_click)
        self.box.add_controller(self.middle_click_controller)
        # right click
        self.right_click_controller = Gtk.GestureSingle()
        self.right_click_controller.set_button(3)
        self.right_click_controller.connect("begin", self.on_right_click)
        self.box.add_controller(self.right_click_controller)

        # Append and set icon and text to widget
        self.box.append(self.icon_label)
        self.box.append(self.text_label)
        self.set_icon()
        self.set_text()

        # Start timer to update the label
        self.update_label()

    def on_scroll(self, controller, x, y):
        pass

    def on_hover_enter(self, controller, x, y):
        pass

    def on_hover_leave(self, controller):
        pass

    def on_click(self, user_data):
        pass

    def on_middle_click(self, sequence, user_data):
        pass

    def on_right_click(self, sequence, user_data):
        pass

    def append(self, widget):
        self.box.append(widget)
        return True

    def set_icon(self):
        self.icon_label.set_markup(f'<span font="{self.icon_size}">{self.icon}</span>')
        return True

    def set_text(self):
        self.text_label.set_label(self.text)
        return True

    def update_label(self):
        GLib.timeout_add(self.timer * 1000, self.set_text)
        return True
