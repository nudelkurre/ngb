from pydbus import SystemBus

import re

from .namedtuples import NamedTuples

BluetoothDevice = NamedTuples.BluetoothDevice


class BluetoothModule:
    system_bus = SystemBus()
    dbus_interface = "org.bluez"
    icons = {"audio-headset": "󰋎", "input-gaming": "󰊗"}

    def __init__(self):
        pass

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
        return BluetoothDevice(
            adapter=device.Adapter if "Adapter" in dir(device) else "",
            address=device.Address if "Address" in dir(device) else "",
            battery=f"{device.Percentage}%" if "Percentage" in dir(device) else "0",
            connected=device.Connected if "Connected" in dir(device) else False,
            icon=self.icons.get(device.Icon, "󰥈"),
            name=device.Name if "Name" in dir(device) else "",
        )

    def get_device_list(self):
        device_list = []
        controllers = self.get_controllers()
        for controller in controllers:
            devices = self.get_devices(controller)
            for device in devices:
                device_info = self.parse_device_info(self.get_device_info(device))
                if device_info.connected:
                    device_list.append(device_info)
        return device_list
