from datetime import datetime
from ngb.modules import NamedTuples
from .weatherbase import Weather_Base

WeatherData = NamedTuples.Weather


class SMHI(Weather_Base):
    def __init__(self, location):
        self.location = location
        super().__init__(self.location)

    def set_url(self):
        self.url = f"https://opendata-download-metfcst.smhi.se/api/category/snow1g/version/1/geotype/point/lon/{self.location[1]}/lat/{self.location[0]}/data.json?timeseries=5&parameters=air_temperature,wind_speed,symbol_code"

    def parse_weather_data(self):
        return_code = self.get_weather_data()
        if return_code == 200:
            res = self.weather_data.get("timeSeries", [{}])
            timeslot = 0
            for i in range(len(res)):
                res_time = datetime.fromisoformat(
                    res[i].get("intervalParametersStartTime", "1970-01-01T00:00:00Z")
                )
                current_time = datetime.now()
                if (
                    res_time.day == current_time.day
                    and res_time.hour == current_time.hour
                ):
                    timeslot = i
                    break
            data = res[timeslot].get("data", {})
            temperature = data.get("air_temperature", 0)
            temperature_unit = "C"
            wind_speed = data.get("wind_speed", 0.0)
            weather_code = data.get("symbol_code", 1)
            icon = self.icons.get(weather_code, "")

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
