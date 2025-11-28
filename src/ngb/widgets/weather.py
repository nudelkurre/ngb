import requests
import json
import time
from datetime import datetime
from tzlocal import get_localzone
from geopy.geocoders import Nominatim
import os
from gi.repository import Gtk
from gi.repository import GLib

from ngb.modules import WidgetBox, DropDownWindow


class Weather_Base:
    city = ""
    location = {"lat": 0, "lon": 0}
    user_agent = "Weather widget"
    url = ""
    weather_data = dict()
    parsed_data = dict()

    icons = {
        1: "☀️",
        2: "🌤️",
        3: "⛅",
        4: "⛅",
        5: "☁️",
        6: "☁️",
        7: "🌫️",
        8: "🌧️",
        9: "🌧️",
        10: "🌧️",
        11: "⛈️",
        12: "🌨️",
        13: "🌨️🌧️",
        14: "🌨️🌧️",
        15: "🌨️",
        16: "🌨️",
        17: "❄️",
        18: "🌧️",
        19: "🌧️",
        20: "🌧️",
        21: "⚡",
        22: "🌨️🌧️",
        23: "🌨️🌧️",
        24: "🌨️🌧️",
        25: "🌨️",
        26: "🌨️",
        27: "🌨️",
    }
    descriptions = {
        1: "Clear sky",
        2: "Nearly clear sky",
        3: "Variable cloudiness",
        4: "Halfclear sky",
        5: "Cloudy sky",
        6: "Overcast",
        7: "Fog",
        8: "Light rain showers",
        9: "Moderate rain showers",
        10: "Heavy rain showers",
        11: "Thunderstorm",
        12: "Light sleet showers",
        13: "Moderate sleet showers",
        14: "Heavy sleet showers",
        15: "Light snow showers",
        16: "Moderate snow showers",
        17: "Heavy snow showers",
        18: "Light rain",
        19: "Moderate rain",
        20: "Heavy rain",
        21: "Thunder",
        22: "Light sleet",
        23: "Moderate sleet",
        24: "Heavy sleet",
        25: "Light snowfall",
        26: "Moderate snowfall",
        27: "Heavy snowfall",
    }

    def __init__(self, **kwargs):
        self.city = kwargs.get("city", "")

    def get_location(self):
        if self.city == "":
            self.city = self.get_city()
        loc = Nominatim(user_agent=self.user_agent)
        g = loc.geocode(self.city)
        self.location["lat"] = float(str(g.latitude)[0:7])
        self.location["lon"] = float(str(g.longitude)[0:7])

    def get_city(self):
        info = requests.get("https://ipconfig.io/json").json()
        city = info["city"]
        return city

    def get_weather_data(self):
        if self.location["lat"] != 0 and self.location["lon"] != 0:
            headers = {"User-Agent": self.user_agent}
            req = requests.get(self.url, headers=headers)
            if req.status_code == 200:
                self.weather_data = req.json()
                return req.status_code
            else:
                return req.status_code

    def parse_weather_data(self):
        pass


class SMHI(Weather_Base):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.get_location()
        self.url = f"https://opendata-download-metfcst.smhi.se/api/category/pmp3g/version/2/geotype/point/lon/{self.location['lon']}/lat/{self.location['lat']}/data.json"

    def parse_weather_data(self):
        data = self.weather_data["timeSeries"][0]["parameters"]
        for d in data:
            if d["name"] == "t":
                self.parsed_data["temperature"] = d["values"][0]
                self.parsed_data["temperature_unit"] = d["unit"][0]
            elif d["name"] == "ws":
                self.parsed_data["wind_speed"] = d["values"][0]
            elif d["name"] == "Wsymb2":
                self.parsed_data["weather_code"] = d["values"][0]


class YR(Weather_Base):
    weather_id = {
        "clearsky": 1,
        "cloudy": 5,
        "fair": 2,
        "fog": 7,
        "heavyrain": 10,
        "heavyrainandthunder": 11,
        "heavyrainshowers": 20,
        "heavyrainshowersandthunder": 11,
        "heavysleet": 24,
        "heavysleetandthunder": 11,
        "heavysleetshowers": 14,
        "heavysleetshowersandthunder": 11,
        "heavysnow": 27,
        "heavysnowandthunder": 11,
        "heavysnowshowers": 17,
        "heavysnowshowersandthunder": 11,
        "lightrain": 18,
        "lightrainandthunder": 11,
        "lightrainshowers": 8,
        "lightrainshowersandthunder": 11,
        "lightsleet": 22,
        "lightsleetandthunder": 11,
        "lightsleetshowers": 12,
        "lightsnow": 25,
        "lightsnowandthunder": 11,
        "lightsnowshowers": 15,
        "lightssleetshowersandthunder": 11,
        "lightssnowshowersandthunder": 11,
        "partlycloudy": 3,
        "rain": 19,
        "rainandthunder": 11,
        "rainshowers": 9,
        "rainshowersandthunder": 11,
        "sleet": 23,
        "sleetandthunder": 11,
        "sleetshowers": 14,
        "sleetshowersandthunder": 11,
        "snow": 26,
        "snowandthunder": 11,
        "snowshowers": 16,
        "snowshowersandthunder": 11,
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.get_location()
        self.url = f"https://api.met.no/weatherapi/locationforecast/2.0/compact?lat={self.location['lat']}&lon={self.location['lon']}"

    def parse_weather_data(self):
        data = self.weather_data["properties"]
        weather = data["timeseries"][0]["data"]
        details = weather["instant"]["details"]
        code = weather["next_1_hours"]["summary"]["symbol_code"]
        units = data["meta"]["units"]
        for d in details:
            if d == "air_temperature":
                self.parsed_data["temperature"] = details[d]
                self.parsed_data["temperature_unit"] = units[d][0].upper()
            elif d == "wind_speed":
                self.parsed_data["wind_speed"] = details[d]
        self.parsed_data["weather_code"] = self.weather_id[code]


class Weather(WidgetBox):
    apis = {
        "smhi": SMHI,
        "yr": YR,
    }

    def __init__(self, **kwargs):
        self.api = kwargs.get("api", "YR")
        self.timer = kwargs.get("timer", 600)
        self.icon_size = kwargs.get("icon_size", 20)
        self.small_text = kwargs.get("small_text_size", 7)
        if self.api.lower() in self.apis:
            self.weather = self.apis.get(self.api.lower())(**kwargs)
        else:
            self.weather = Weather_Base()
        super().__init__(timer=self.timer, icon_size=self.icon_size)
        self.city_label = Gtk.Label()
        self.city_label.set_label(self.weather.city)
        self.weather_icon = Gtk.Label()
        self.temperature_label = Gtk.Label()
        self.wind_speed_label = Gtk.Label()
        self.weather_description_label = Gtk.Label()
        self.api_label = Gtk.Label()
        self.api_label.set_markup(
            f"<span font='{self.small_text}'>API in use: {self.api}</span>"
        )
        self.last_updated_label = Gtk.Label(label="test")
        self.populate_dropdown()
        self.update_weather()
        self.update_timeout()

    def on_click(self, user_data):
        if not (
            isinstance(self.weather, Weather_Base)
            and type(self.weather) is Weather_Base
        ):
            self.dropdown.popup()
        return True

    def populate_dropdown(self):
        self.dropdown.add(self.city_label)
        self.dropdown.add(self.weather_icon)
        self.dropdown.add(self.temperature_label)
        self.dropdown.add(self.wind_speed_label)
        self.dropdown.add(self.weather_description_label)
        self.dropdown.add(self.api_label)
        self.dropdown.add(self.last_updated_label)
        return True

    def set_text(self):
        if (
            isinstance(self.weather, Weather_Base)
            and type(self.weather) is Weather_Base
        ):
            self.text_label.set_label("No API set")
        else:
            parsed_data = self.weather.parsed_data
            if "temperature" in parsed_data:
                temperature = (
                    f"{parsed_data['temperature']} {parsed_data['temperature_unit']}"
                )
                self.text_label.set_label(temperature)
                self.icon = self.weather.icons[parsed_data["weather_code"]]
                self.set_icon()
                self.temperature_label.set_label(f"Temperature {temperature}")
            if "wind_speed" in parsed_data:
                self.wind_speed_label.set_label(
                    f"Wind speed {parsed_data['wind_speed']} m/s"
                )
            if "weather_code" in parsed_data:
                self.weather_description_label.set_label(
                    f"{self.weather.descriptions[parsed_data['weather_code']]}"
                )
                self.weather_icon.set_markup(
                    f'<span font="{self.icon_size}">{self.weather.icons[parsed_data["weather_code"]]}</span>'
                )
        return True

    def update_weather(self):
        return_code = self.weather.get_weather_data()
        if return_code == 200:
            self.weather.parse_weather_data()
            self.set_text()
            self.last_updated_label.set_markup(
                f'<span font="{self.small_text}">Last updated: {datetime.now().strftime("%H:%M")}</span>'
            )
        return True

    def update_timeout(self):
        GLib.timeout_add(self.timer * 1000, self.update_weather)
