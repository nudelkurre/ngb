import psutil


class BatteryModule:
    def __init__(self):
        self.battery = psutil.sensors_battery()

    def is_charging(self):
        if self.battery is not None:
            return self.battery.power_plugged
        else:
            return False

    def get_battery_level(self):
        if self.battery == None:
            return ""
        return str(int(self.battery.percent))

    def get_battery_icon(self):
        if self.battery == None:
            return "󱃍"
        charging = self.is_charging()
        if charging:
            if self.battery.percent == 100:
                return "󰚥"
            elif self.battery.percent >= 75:
                return "󱊦"
            elif self.battery.percent >= 50:
                return "󱊥"
            elif self.battery.percent >= 25:
                return "󱊤"
            else:
                return "󰢟"
        else:
            if self.battery.percent >= 75:
                return "󱊣"
            elif self.battery.percent >= 50:
                return "󱊢"
            elif self.battery.percent >= 25:
                return "󱊡"
            else:
                return "󰂎"
