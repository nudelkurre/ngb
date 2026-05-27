from gi.repository import Gtk
from gi.repository import GLib

from ngb.modules import BluetoothModule, WidgetBox


class Bluetooth(Gtk.Box):

    def __init__(self, **kwargs):
        self.timer = kwargs.get("timer", 5)
        self.spacing = kwargs.get("spacing", 10)
        self.icon_size = kwargs.get("icon_size", 20)
        self.devices = BluetoothModule()
        super().__init__(spacing=self.spacing)
        self.is_stopped = False
        self.timeout = None

    def run(self):
        self.update_boxes()
        self.update_list()

    def stop(self):
        self.is_stopped = True
        if self.timeout:
            GLib.source_remove(self.timeout)
            self.timeout = None

    def remove_widget(self):
        parent = self.get_parent()
        if parent:
            parent.remove(self)

    def update_boxes(self):
        while self.get_first_accessible_child() is not None:
            self.remove(self.get_first_accessible_child())
        device_list = self.devices.get_device_list()
        for device in device_list:
            bluetooth_box = WidgetBox(
                icon=device.icon,
                text=device.battery,
                spacing=self.spacing,
                icon_size=self.icon_size,
            )
            bluetooth_box.run()
            self.append(bluetooth_box)

        return True

    def update_list(self):
        self.timeout = GLib.timeout_add(self.timer * 1000, self.update_boxes)
        return True
