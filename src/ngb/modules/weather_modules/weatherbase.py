import requests


class Weather_Base:
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

    def __init__(self, location):
        self.location = location
        self.user_agent = "Weather widget"
        self.url = ""
        self.error = True
        self.weather_data = dict()
        self.parsed_data = dict()

    def set_url(self):
        pass

    def get_weather_data(self):
        if self.location != (0.0, 0.0):
            headers = {"User-Agent": self.user_agent}
            if self.url:
                try:
                    req = requests.get(self.url, headers=headers)
                    if req.status_code == 200:
                        self.weather_data = req.json()
                        return req.status_code
                    else:
                        return req.status_code
                except requests.exceptions.ConnectionError:
                    return -1
            else:
                return -2
        return -3

    def parse_weather_data(self):
        pass
