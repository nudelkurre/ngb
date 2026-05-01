from datetime import datetime
from ngb.types import NamedTuples
from .weatherbase import Weather_Base

WeatherData = NamedTuples.Weather


class YR(Weather_Base):
    weather_id = {
        "clearsky_day": 1,
        "clearsky_night": 1,
        "clearsky_polartwilight": 1,
        "fair_day": 2,
        "fair_night": 2,
        "fair_polartwilight": 2,
        "partlycloudy_day": 3,
        "partlycloudy_night": 3,
        "partlycloudy_polartwilight": 3,
        "cloudy": 5,
        "rainshowers_day": 9,
        "rainshowers_night": 9,
        "rainshowers_polartwilight": 9,
        "rainshowersandthunder_day": 11,
        "rainshowersandthunder_night": 11,
        "rainshowersandthunder_polartwilight": 11,
        "sleetshowers_day": 13,
        "sleetshowers_night": 13,
        "sleetshowers_polartwilight": 13,
        "snowshowers_day": 16,
        "snowshowers_night": 16,
        "snowshowers_polartwilight": 16,
        "rain": 19,
        "heavyrain": 20,
        "heavyrainandthunder": 11,
        "sleet": 23,
        "snow": 26,
        "snowandthunder": 11,
        "fog": 7,
        "sleetshowersandthunder_day": 11,
        "sleetshowersandthunder_night": 11,
        "sleetshowersandthunder_polartwilight": 11,
        "snowshowersandthunder_day": 11,
        "snowshowersandthunder_night": 11,
        "snowshowersandthunder_polartwilight": 11,
        "rainandthunder": 11,
        "sleetandthunder": 11,
        "lightrainshowersandthunder_day": 11,
        "lightrainshowersandthunder_night": 11,
        "lightrainshowersandthunder_polartwilight": 11,
        "heavyrainshowersandthunder_day": 11,
        "heavyrainshowersandthunder_night": 11,
        "heavyrainshowersandthunder_polartwilight": 11,
        "lightssleetshowersandthunder_day": 11,
        "lightssleetshowersandthunder_night": 11,
        "lightssleetshowersandthunder_polartwilight": 11,
        "heavysleetshowersandthunder_day": 11,
        "heavysleetshowersandthunder_night": 11,
        "heavysleetshowersandthunder_polartwilight": 11,
        "lightssnowshowersandthunder_day": 11,
        "lightssnowshowersandthunder_night": 11,
        "lightssnowshowersandthunder_polartwilight": 11,
        "heavysnowshowersandthunder_day": 11,
        "heavysnowshowersandthunder_night": 11,
        "heavysnowshowersandthunder_polartwilight": 11,
        "lightrainandthunder": 11,
        "lightsleetandthunder": 11,
        "heavysleetandthunder": 11,
        "lightsnowandthunder": 11,
        "heavysnowandthunder": 11,
        "lightrainshowers_day": 8,
        "lightrainshowers_night": 8,
        "lightrainshowers_polartwilight": 8,
        "heavyrainshowers_day": 10,
        "heavyrainshowers_night": 10,
        "heavyrainshowers_polartwilight": 10,
        "lightsleetshowers_day": 12,
        "lightsleetshowers_night": 12,
        "lightsleetshowers_polartwilight": 12,
        "heavysleetshowers_day": 14,
        "heavysleetshowers_night": 14,
        "heavysleetshowers_polartwilight": 14,
        "lightsnowshowers_day": 15,
        "lightsnowshowers_night": 15,
        "lightsnowshowers_polartwilight": 15,
        "heavysnowshowers_day": 17,
        "heavysnowshowers_night": 17,
        "heavysnowshowers_polartwilight": 17,
        "lightrain": 18,
        "lightsleet": 22,
        "heavysleet": 24,
        "lightsnow": 25,
        "heavysnow": 27,
    }

    def __init__(self, location):
        self.location = location
        super().__init__(self.location)

    def set_url(self):
        self.url = f"https://api.met.no/weatherapi/locationforecast/2.0/compact?lat={self.location[0]}&lon={self.location[1]}"

    def parse_weather_data(self):
        return_code = self.get_weather_data()
        if return_code == 200:
            data = self.weather_data.get("properties", {})
            res = data.get("timeseries", [{}])
            timeslot = 0
            for t in range(len(res)):
                res_time = datetime.fromisoformat(
                    res[t].get("time", "1970-01-01T00:00:00Z")
                )
                current_time = datetime.now()
                if (
                    res_time.day == current_time.day
                    and res_time.hour == current_time.hour
                ):
                    timeslot = t
                    break
            weather = res[timeslot].get("data", {})
            details = weather.get("instant", {}).get("details", {})
            code = (
                weather.get("next_1_hours", {})
                .get("summary", {})
                .get("symbol_code", None)
            )
            units = data.get("meta", {}).get("units", None)

            temperature = details.get("air_temperature", 0)
            temperature_unit = "C"
            wind_speed = details.get("wind_speed", 0.0)
            weather_code = self.weather_id.get(code, 1)
            icon = self.icons.get(weather_code, 1)

            self.error = False

            return WeatherData(
                temperature=temperature,
                temperature_unit=temperature_unit,
                windspeed=wind_speed,
                weather_code=weather_code,
                icon=icon,
            )
        else:
            self.error = True
            return WeatherData(
                error=f"{return_code}: {self.connection_errors.get(return_code, "Error")}"
            )
