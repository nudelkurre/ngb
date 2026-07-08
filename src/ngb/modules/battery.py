import psutil


class BatteryModule:
    def update_battery(self):
        return psutil.sensors_battery()

    def is_charging(self):
        battery = self.update_battery()
        if battery is not None:
            return battery.power_plugged
        else:
            return False

    def get_battery_level(self):
        battery = self.update_battery()
        if battery == None:
            return ""
        return str(int(battery.percent))

    def get_battery_icon(self):
        battery = self.update_battery()
        if battery == None:
            return "󱃍"
        charging = self.is_charging()
        if charging:
            if battery.percent == 100:
                return "󰚥"
            elif battery.percent >= 75:
                return "󱊦"
            elif battery.percent >= 50:
                return "󱊥"
            elif battery.percent >= 25:
                return "󱊤"
            else:
                return "󰢟"
        else:
            if battery.percent >= 75:
                return "󱊣"
            elif battery.percent >= 50:
                return "󱊢"
            elif battery.percent >= 25:
                return "󱊡"
            else:
                return "󰂎"
