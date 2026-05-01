from gi.repository import Gtk
from gi.repository import GLib

from ngb.modules import WeatherModule, WidgetBox, DropDownWindow


class Weather(WidgetBox):

    def __init__(self, **kwargs):
        self.api = kwargs.get("api", "YR")
        self.timer = kwargs.get("timer", 600)
        self.icon_size = kwargs.get("icon_size", 20)
        self.small_text = kwargs.get("small_text_size", 7)
        self.show_big_icon = kwargs.get("show_big_icon", False)
        self.big_icon_size = kwargs.get("big_icon_size", 60)
        self.big_icon = Gtk.Label()
        self.weather_data = None
        self.weather_api = WeatherModule(self.api, kwargs.get("city"))
        super().__init__(timer=self.timer, icon_size=self.icon_size)

        self.api_label = Gtk.Label()
        self.api_label.set_markup(
            f"<span font='{self.small_text}'>API in use: {self.api}</span>"
        )
        self.last_updated_label = Gtk.Label()

    def run(self):
        super().run()

    def on_click(self, user_data):
        if self.weather_data and self.weather_data.error is None:
            self.dropdown.popup()
        return True

    def populate_dropdown(self):
        self.dropdown.add(Gtk.Label(label=self.weather_api.city))
        if self.show_big_icon:
            self.dropdown.add(self.big_icon)
            self.set_big_icon()
        self.dropdown.add(
            Gtk.Label(label=f"Temperature {self.weather_data.temperature}")
        )
        self.dropdown.add(
            Gtk.Label(label=f"Wind speed {self.weather_data.windspeed} m/s")
        )
        self.dropdown.add(
            Gtk.Label(
                label=self.weather_api.get_description(self.weather_data.weather_code)
            )
        )
        self.dropdown.add(self.api_label)
        self.set_last_update_label()
        self.dropdown.add(self.last_updated_label)
        return True

    def set_big_icon(self):
        self.big_icon.set_markup(
            f"<span font='{self.big_icon_size}'>{self.weather_data.icon}</span>"
        )

    def set_last_update_label(self):
        self.last_updated_label.set_markup(
            f"<span font='{self.small_text}'>Last updated: {self.weather_api.last_updated}</span>"
        )

    def set_text(self):
        self.weather_data = self.weather_api.get_weather()
        if self.weather_data:
            if self.weather_data.error is None:
                if self.text_label.get_visible() == False:
                    self.text_label.set_visible(True)
                self.text_label.set_label(
                    f"{self.weather_data.temperature} {self.weather_data.temperature_unit}"
                )
                self.icon = self.weather_data.icon
                self.set_icon()
            else:
                self.text_label.set_visible(False)
                self.icon = ""
                self.set_icon()
                self.set_tooltip_text(self.weather_data.error)
        return True
