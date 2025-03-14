import requests
import json
import time
from datetime import datetime
from tzlocal import get_localzone
from geopy.geocoders import Nominatim
import os

from ngb.modules import WidgetBox

class Weather(WidgetBox):
    lat = 0
    lon = 0
    user_agent = "Weather widget"
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
        27: "🌨️"
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
        27: "Heavy snowfall"
    }

    def __init__(self, **kwargs):
        self.city = kwargs.get("city", "")
        self.timer = kwargs.get("timer", 600)
        super().__init__(timer=self.timer)
        if(self.city == ""):
            self.text_label.set_label("City not set")
        else:
            self.get_location()
            self.get_weather_data()
            self.parse_weather_data()
            self.set_text()

    def get_location(self):
        loc = Nominatim(user_agent=self.user_agent)
        g = loc.geocode(self.city)
        self.lat = float(str(g.latitude)[0:7])
        self.lon = float(str(g.longitude)[0:7])
        return True

    def get_weather_data(self):
        if(self.lat != 0 and self.lon != 0):
            headers = {
                'User-Agent': self.user_agent
            }
            url = f"https://opendata-download-metfcst.smhi.se/api/category/pmp3g/version/2/geotype/point/lon/{self.lon}/lat/{self.lat}/data.json"
            req = requests.get(url, headers=headers)
            if(req.status_code == 200):
                self.weather_data = req.json()
            else:
                self.text_label.set_label(req.status_code)

    def parse_weather_data(self):
        data = self.weather_data["timeSeries"][0]["parameters"]
        # print(data)
        for d in data:
            if(d["name"] == "t"):
                self.parsed_data["temperature"] = d["values"][0]
                self.parsed_data["temperature_unit"] = d["unit"][0]
            elif(d["name"] == "ws"):
                self.parsed_data["wind_speed"] = d["values"][0]
            elif(d["name"] == "Wsymb2"):
                self.parsed_data["weather_code"] = d["values"][0]

    def set_text(self):
        if("temperature" in self.parsed_data):
            self.text_label.set_label(f"{self.parsed_data['temperature']} {self.parsed_data['temperature_unit']}")
            self.icon = self.icons[self.parsed_data["weather_code"]]
            self.set_icon()
        return True