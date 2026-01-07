from gi.repository import Gtk
from gi.repository import GLib
from pydbus import SystemBus

import re

from ngb.modules import WidgetBox


class Bluetooth(Gtk.Box):
    system_bus = SystemBus()
    dbus_interface = "org.bluez"
    icons = {"audio-headset": "󰋎", "input-gaming": "󰊗"}

    def __init__(self, **kwargs):
        self.timer = kwargs.get("timer", 5)
        self.spacing = kwargs.get("spacing", 10)
        self.icon_size = kwargs.get("icon_size", 20)
        super().__init__(spacing=self.spacing)
        self.update_boxes()
        self.update_list()

    def update_boxes(self):
        while self.get_first_accessible_child() is not None:
            self.remove(self.get_first_accessible_child())
        controllers = self.get_controllers()
        for controller in controllers:
            devices = self.get_devices(controller)
            for device in devices:
                device = self.get_device_info(device)
                device_info = self.parse_device_info(device)
                if device_info["connected"]:
                    self.append(
                        WidgetBox(
                            icon=device_info["icon"],
                            text=f"{device_info['battery']}%",
                            spacing=self.spacing,
                            icon_size=self.icon_size,
                        )
                    )

        return True

    def get_controllers(self):
        proxy = self.system_bus.get(self.dbus_interface)
        proxy_data = proxy.Introspect()
        controllers = re.findall(r"<node name=\"([\w]+)\"/>", proxy_data)
        return controllers

    def get_devices(self, controller):
        proxy = self.system_bus.get(self.dbus_interface, controller)
        proxy_data = proxy.Introspect()
        devices = re.findall(r"<node name=\"([\w]+)\"/>", proxy_data)
        device_controller = []
        for device in devices:
            device_controller.append((controller, device))
        return device_controller

    def get_device_info(self, device):
        object_path = f"{device[0]}/{device[1]}"
        proxy = self.system_bus.get(self.dbus_interface, object_path)
        proxy_data = proxy
        return proxy_data

    def parse_device_info(self, device):
        adapter = device.Adapter if "Adapter" in dir(device) else ""
        address = device.Address if "Address" in dir(device) else ""
        battery = device.Percentage if "Percentage" in dir(device) else "0"
        connected = device.Connected if "Connected" in dir(device) else False
        icon = self.icons[device.Icon] if "Icon" in dir(device) else ""
        name = device.Name if "Name" in dir(device) else ""
        return {
            "adapter": adapter,
            "address": address,
            "battery": battery,
            "connected": connected,
            "icon": icon,
            "name": name,
        }

    def update_list(self):
        GLib.timeout_add(self.timer * 1000, self.update_boxes)
        return True
