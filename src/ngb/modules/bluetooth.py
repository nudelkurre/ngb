from gi.repository import GLib, Gio

import re

from ngb.types import NamedTuples

BluetoothDevice = NamedTuples.BluetoothDevice


class BluetoothModule:
    icons = {"audio-headset": "󰋎", "input-gaming": "󰊗"}

    def __init__(self):
        pass

    def get_device_list(self):
        device_list = []
        bus_type = Gio.BusType.SYSTEM
        bus_name = "org.bluez"
        object_path = "/"
        mngr_iface = "org.freedesktop.DBus.ObjectManager"
        device_iface = "org.bluez.Device1"
        battery_iface = "org.bluez.Battery1"

        mngr_proxy = Gio.DBusProxy.new_for_bus_sync(
            bus_type=bus_type,
            flags=Gio.DBusProxyFlags.NONE,
            info=None,
            name=bus_name,
            object_path=object_path,
            interface_name=mngr_iface,
            cancellable=None,
        )

        mngd_objs = mngr_proxy.GetManagedObjects()
        for obj_path, obj_data in mngd_objs.items():
            obj_data_device = obj_data.get(device_iface, {})
            if obj_data_device:
                if obj_data_device.get("Connected"):
                    device_battery_data = obj_data.get(battery_iface, {})
                    device_list.append(
                        BluetoothDevice(
                            adapter=obj_data_device.get("Adapter", ""),
                            address=obj_data_device.get("Address", ""),
                            battery=f"{device_battery_data.get("Percentage", "0")}%",
                            connected=obj_data_device.get("Connected", False),
                            icon=self.icons.get(obj_data_device.get("Icon"), "󰥉"),
                            name=obj_data_device.get("Name", ""),
                        )
                    )
        return device_list
