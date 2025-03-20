from gi.repository import Gtk
from gi.repository import GLib
from datetime import datetime

from ngb.modules import WidgetBox

class Clock(WidgetBox):
    timeformat = ""
    def __init__(self, **kwargs):
        self.icon = kwargs.get("icon", "")
        self.spacing = kwargs.get("spacing", 4)
        self.timer = kwargs.get("timer", 1)
        self.timeformat = kwargs.get("timeformat_normal", "%T")
        self.timeformat_revealer = kwargs.get("timeformat_revealer", "%A %Y-%m-%d")
        self.transition_time = kwargs.get("transition_time", 500)
        self.icon_size = kwargs.get("icon_size", 20)
        self.show_day_names = kwargs.get("show_day_names", True)
        self.show_heading = kwargs.get("show_heading", True)
        self.show_week_numbers = kwargs.get("show_week_numbers", True)
        self.revealer_label = Gtk.Label()
        self.show_revealer = False
        super().__init__(icon=self.icon, spacing=self.spacing, timer=self.timer, icon_size=self.icon_size)
        self.populate_dropdown()
        
        # Create a revealer for smoother transition when hover over
        self.revealer = Gtk.Revealer()
        self.revealer.set_child(self.revealer_label)
        self.revealer.set_transition_type(Gtk.RevealerTransitionType.SLIDE_LEFT)
        self.revealer.set_transition_duration(self.transition_time)
        self.box.insert_child_after(self.revealer, self.icon_label)

    def populate_dropdown(self):
        calendar = Gtk.Calendar()
        calendar.set_show_day_names(self.show_day_names)
        calendar.set_show_heading(self.show_heading)
        calendar.set_show_week_numbers(self.show_week_numbers)
        self.dropdown.add(calendar)

    def set_text(self):
        datetimenow = datetime.now().strftime(self.timeformat)
        datetimenow_revealer = datetime.now().strftime(self.timeformat_revealer)
        self.text_label.set_text(datetimenow)
        self.revealer_label.set_text(datetimenow_revealer)
        return True

    def on_click(self, user_data):
        self.show_revealer = not self.show_revealer
        self.revealer.set_reveal_child(self.show_revealer)

    def on_right_click(self, sequence, user_data):
        self.dropdown.popup()
