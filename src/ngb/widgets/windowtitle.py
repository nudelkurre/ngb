from gi.repository import Gtk
from gi.repository import GLib

from ngb.modules import IPCModule, WidgetBox
from ngb.utils import cut_string_length


class WindowButton(Gtk.Box):
    def __init__(self, **kwargs):
        super().__init__()
        self.window = kwargs.get("window", {})
        self.wm = kwargs.get("wm")
        self.dropdown = kwargs.get("dropdown")
        self.hide_on_close = kwargs.get("hide_on_close")
        self.window_title = kwargs.get("title", "")
        self.window_id = kwargs.get("id")
        self.title_max_length = kwargs.get("title_max_length", 200)
        self.window_button = Gtk.Button(label=self.window_title)
        self.window_button.add_css_class("widget-button")
        self.window_button.connect("clicked", self.focus_window)
        self.append(self.window_button)

        self.close_button = Gtk.Button(label="X")
        self.close_button.connect("clicked", self.close_window)
        self.append(self.close_button)

    def close_window(self, user_data):
        self.wm.close_window(self.window_id)
        self.dropdown.remove(self)
        if self.hide_on_close:
            self.dropdown.popdown()

    def focus_window(self, user_data):
        self.wm.focus_window(self.window_id)
        self.dropdown.popdown()


class WindowTitle(WidgetBox):

    def __init__(self, **kwargs):
        super().__init__(icon="", spacing=1)
        self.timer = kwargs.get("timer", 0.1)
        self.hide_no_focus = kwargs.get("hide_no_focus", False)
        self.hide_on_close = kwargs.get("hide_on_close", True)
        self.title_max_length = kwargs.get("title_max_length", 200)
        self.wm_api = IPCModule(timer=self.timer, **kwargs)
        self.wm_api.connect("window-updates", self.on_window_updates)
        self.wm_api.connect("focused-window-updates", self.on_focused_window_updates)

        self.focused_title = ""
        self.windows = []

        self.update_label()

    def on_window_updates(self, instance, data):
        self.windows = data

    def on_focused_window_updates(self, instance, data):
        self.focused_title = data.title
        self.update_label()

    def run(self):
        pass

    def populate_dropdown(self):
        for window in self.windows:
            self.dropdown.add(
                WindowButton(
                    title=cut_string_length(window.title, self.title_max_length),
                    id=window.id,
                    wm=self.wm_api,
                    dropdown=self.dropdown,
                    hide_on_close=self.hide_on_close,
                )
            )

    def on_click(self, user_data):
        if self.wm_api.is_valid_wm():
            self.dropdown.popup()
        return True

    def _task_func(self, task, _task_data, _cancellable, _other):
        data = {"text": self.focused_title}
        task.return_value(data)
