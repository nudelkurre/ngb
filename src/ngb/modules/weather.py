from datetime import datetime
import geopy
from geopy.geocoders import Nominatim
import requests

from .namedtuples import NamedTuples
from .weather_modules import SMHI, Weather_Base, YR

WeatherData = NamedTuples.Weather


class WeatherModule:
    valid_apis = {"smhi": SMHI, "yr": YR}
    user_agent = "Weather widget"

    connection_errors = {
        -1: "No connection",
        -2: "No url set",
        -3: "Location is not set",
        404: "URL not found",
    }

    def __init__(self, api, city):
        self.api = api.lower()
        self.city = city
        self.location = {"lat": 0.0, "lon": 0.0}
        self.get_location()
        self.last_updated = 0
        self.weather = self.valid_apis.get(self.api, Weather_Base)(self.location)

    def get_city(self):
        try:
            info = requests.get("https://ipconfig.io/json").json()
            city = info["city"]
            return city
        except requests.exceptions.ConnectionError:
            print("No location set because of connection error")
            return None

    def get_description(self, code):
        return self.weather.descriptions.get(code, self.weather.descriptions.get(1))

    def get_location(self):
        if self.city == "":
            self.city = self.get_city()
        try:
            loc = Nominatim(user_agent=self.user_agent)
            g = loc.geocode(self.city)
            self.location = (float(str(g.latitude)[0:7]), float(str(g.longitude)[0:7]))
        except geopy.exc.GeocoderUnavailable:
            print("Can not connect to Nominatim")

    def get_weather(self):
        self.weather.set_url()
        res_code = self.weather.get_weather_data()
        if res_code == 200:
            self.last_updated = datetime.now().strftime("%H:%M")
            return self.weather.parse_weather_data()
        else:
            return WeatherData(error=self.connection_errors.get(res_code, "Error"))
