from gi.repository import Gtk
from gi.repository import GLib
from gi.repository import Gio

from .widgetbox import WidgetBox


class WidgetDrawer(Gtk.Box):
    def __init__(self, **kwargs):
        self.spacing = kwargs.get("spacing", 5)
        super().__init__(spacing=self.spacing)
        self.timer = kwargs.get("timer", 0.1)
        self.old_boxes = []
        self.new_boxes = []

        self.is_stopped = False

        # Store the running timer to be able to stop it
        self.timeout = None

        # Prevent overlapping tasks if one already running
        self._task_in_flight = False

        # Add scroll controller to use scroll events
        self.scroll_controller = Gtk.EventControllerScroll.new(
            Gtk.EventControllerScrollFlags.VERTICAL
        )
        self.scroll_controller.connect("scroll", self.on_scroll)
        self.add_controller(self.scroll_controller)

    def run(self):
        self.update_boxes()
        if getattr(self, "timeout", None) is not None:
            return False
        self.timeout = GLib.timeout_add(self.timer * 1000, self.update_boxes)
        return True

    def stop(self):
        self.is_stopped = True
        if self.timeout:
            GLib.source_remove(self.timeout)
            self.timeout = None

    def cleanup(self):
        child = self.get_first_child()
        while child:
            child.stop()
            child.unparent()
            child = self.get_first_child()

    def get_boxes(self):
        return [{"name": "1", "icon": "!"}, {"name": "2", "icon": "@"}]

    def create_widget(self, box):
        return None

    def _task_func(self, task, _task_data, _cancellable, _other):
        data = self.get_boxes()
        task.return_value(data)

    def _on_task_ready(self, task, _result, _user_data=None):
        try:
            self.new_boxes = _result.propagate_value()[1]
            if self.new_boxes != self.old_boxes:
                if self.get_first_child() is not None:
                    self.cleanup()
                self.old_boxes = self.new_boxes
                if len(self.old_boxes) == 0:
                    self.set_visible(False)
                else:
                    self.set_visible(True)
                    for box in self.old_boxes:
                        widget = self.create_widget(box)
                        if widget is not None:
                            self.append(widget)
                            widget.run()
        except Exception as e:
            pass
        finally:
            self._task_in_flight = False

    def update_boxes(self):
        if self._task_in_flight:
            return True
        self._task_in_flight = True
        self._task = Gio.Task.new(self, None, self._on_task_ready, None)
        self._task.run_in_thread(self._task_func)
        return True

    def on_scroll(self, controller, x, y):
        pass
