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
        self.text = kwargs.get("text", "Default text")
        self.icon = kwargs.get("icon", "?")
        self.icon_size = kwargs.get("icon_size", 20)
        super().__init__()

        # Set css class to use the custom css created
        self.add_css_class("widget-button")

        # Create labels for icon and text for button
        self.icon_label = Gtk.Label()
        self.icon_label.add_css_class("icon")
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

        # Connect signals for dropdown
        self.dropdown.connect("show", self.on_show)
        self.dropdown.connect("closed", self.on_close)

        # Append icon and text to widget
        self.box.append(self.icon_label)
        self.box.append(self.text_label)

        # Store the running timer to be able to stop it
        self.timeout = None

        # Prevent overlapping tasks if one already running
        self._task_in_flight = False

        # Check if widget is stopped
        self.is_stopped = False

    def run(self):
        self.update_label()
        if getattr(self, "timeout", None) is not None:
            return False
        self.timeout = GLib.timeout_add(self.timer * 1000, self.update_label)
        return True

    def stop(self):
        self.is_stopped = True
        if self.timeout:
            GLib.source_remove(self.timeout)
            self.timeout = None

    def remove_widget(self):
        parent = self.get_parent()
        if parent:
            parent.remove(self)

    def populate_dropdown(self):
        pass

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

    def on_show(self, user_data):
        self.populate_dropdown()

    def on_close(self, user_data):
        self.dropdown.clear()

    def append(self, widget):
        self.box.append(widget)
        return True

    def _task_func(self, task, _task_data, _cancellable, _other):
        data = {"text": self.text, "icon": self.icon}
        task.return_value(data)

    def _on_task_ready(self, task, _result, _user_data=None):
        try:
            task_dict = _result.propagate_value()[1]
            if task_dict.get("text", "") == "":
                self.text_label.set_visible(False)
            else:
                self.text_label.set_visible(True)
            if task_dict.get("icon", "") == "":
                self.icon_label.set_visible(False)
            else:
                self.icon_label.set_visible(True)
            self.text_label.set_label(task_dict.get("text", "Default text"))
            self.icon_label.set_label(task_dict.get("icon", "?"))
            self.set_tooltip_text(task_dict.get("tooltip", ""))
        except Exception as e:
            pass
        finally:
            self._task_in_flight = False

    def update_label(self):
        if self._task_in_flight:
            return True
        self._task_in_flight = True
        self._task = Gio.Task.new(self, None, self._on_task_ready, None)
        self._task.run_in_thread(self._task_func)
        return True
