from gi.repository import Gtk
from gi.repository import GLib

from ngb.modules import NetworkModule, WidgetBox


class Network(WidgetBox):

    def __init__(self, **kwargs):
        self.interface_name = kwargs.get("interface", "")

        self.timer = kwargs.get("timer", 10)
        self.icon = kwargs.get("icon", "󰈀")
        self.icon_size = kwargs.get("icon_size", 20)
        self.interface = NetworkModule(self.interface_name)

        self.show_public_ip = kwargs.get("show_public_ip", True)
        self.show_ipv6 = kwargs.get("show_ipv6", False)
        self.show_disconnected = kwargs.get("show_disconnected", False)
        super().__init__(icon=self.icon, timer=self.timer, icon_size=self.icon_size)

    def run(self):
        super().run()
        self.dropdown.connect("closed", self.on_close)

    def set_text(self):
        if self.interface.is_up():
            self.set_visible(True)
        else:
            self.set_visible(self.show_disconnected)
        self.text_label.set_label(self.interface.get_ipv4_addr())
        return True

    def populate_dropdown(self):
        self.dropdown.add(Gtk.Label(label=f"Interface: {self.interface_name}"))
        self.dropdown.add(Gtk.Label(label=f"MAC: {self.interface.get_mac_address()}"))
        if self.show_public_ip:
            self.dropdown.add(
                Gtk.Label(label=f"Public IP: {self.interface.get_public_ip()}")
            )
        self.dropdown.add(Gtk.Label(label=f"IPv4: {self.interface.get_ipv4_addr()}"))
        if self.show_ipv6:
            ipv6_label = Gtk.Label()
            ipv6_label.add_css_class("multi-line")
            self.dropdown.add(Gtk.Label(label="IPv6:"))
            ipv6_label.set_label("\n".join(self.interface.get_ipv6_addrs()))
            self.dropdown.add(ipv6_label)

    def on_click(self, user_data):
        if self.interface.is_up():
            self.populate_dropdown()
            self.dropdown.popup()
        return True

    def on_close(self, user_data):
        self.dropdown.clear()
        return True
