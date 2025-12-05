from gi.repository import Gtk
from gi.repository import GLib
import psutil
import socket
import requests

from ngb.modules import WidgetBox


class Network(WidgetBox):
    interface = []

    def __init__(self, **kwargs):
        self.interface_name = kwargs.get("interface", "")
        self.interface = (
            psutil.net_if_addrs()[self.interface_name]
            if self.interface_name in psutil.net_if_addrs()
            else []
        )
        self.is_up = (
            psutil.net_if_stats()[self.interface_name].isup
            if self.interface_name in psutil.net_if_stats()
            else False
        )
        self.timer = kwargs.get("timer", 10)
        self.icon = kwargs.get("icon", "󰈀")
        self.icon_size = kwargs.get("icon_size", 20)
        self.show_public_ip = kwargs.get("show_public_ip", True)
        self.show_ipv6 = kwargs.get("show_ipv6", False)
        self.interface_label = Gtk.Label(label=f"Interface: {self.interface_name}")
        self.public_ip_header_label = Gtk.Label(label="Public IP:")
        self.public_ip_label = Gtk.Label()
        self.public_ip_label.set_justify(Gtk.Justification.CENTER)
        self.ipv4_header_label = Gtk.Label(label="IPv4:")
        self.ipv6_header_label = Gtk.Label(label="IPv6:")
        self.ipv4_label = Gtk.Label()
        self.ipv4_label.set_justify(Gtk.Justification.CENTER)
        self.ipv6_label = Gtk.Label()
        self.ipv6_label.set_justify(Gtk.Justification.CENTER)
        self.ipv6_label.add_css_class("multi-line")
        self.mac_address_label = Gtk.Label()
        super().__init__(icon=self.icon, timer=self.timer, icon_size=self.icon_size)
        self.dropdown.connect("closed", self.on_close)

    def set_text(self):
        self.get_ipv4_addr()
        return True

    def populate_dropdown(self):
        self.dropdown.add(self.interface_label)
        self.get_mac_address()
        self.dropdown.add(self.mac_address_label)
        if self.show_public_ip:
            self.get_public_ip()
            self.dropdown.add(self.public_ip_header_label)
            self.dropdown.add(self.public_ip_label)
        self.dropdown.add(self.ipv4_header_label)
        self.dropdown.add(self.ipv4_label)
        if self.show_ipv6:
            self.get_ipv6_addrs()
            self.dropdown.add(self.ipv6_header_label)
            self.dropdown.add(self.ipv6_label)

    def get_ipv4_addr(self):
        if self.is_up:
            address = ""
            for addr in self.interface:
                if addr.family == socket.AF_INET and address == "":
                    address = addr.address
            if address != "":
                self.text_label.set_label(address)
                self.ipv4_label.set_label(address)
                self.ipv4_label.set_visible(True)
                self.ipv4_header_label.set_visible(True)
            else:
                self.text_label.set_label("N/A")
                self.ipv4_label.set_visible(False)
                self.ipv4_header_label.set_visible(False)
        else:
            self.text_label.set_label("Not connected")
        return True

    def get_ipv6_addrs(self):
        addrs = []
        for addr in self.interface:
            if addr.family == socket.AF_INET6:
                addrs.append(addr.address)
        if len(addrs) > 0:
            self.ipv6_label.set_label("\n".join(addrs))
            self.ipv6_label.set_visible(True)
            self.ipv6_header_label.set_visible(True)
        else:
            self.ipv6_label.set_visible(False)
            self.ipv6_header_label.set_visible(False)
        return True

    def get_public_ip(self):
        req = requests.get("https://ipinfo.io").json()
        self.public_ip_label.set_label(req.get("ip"))
        return True

    def get_mac_address(self):
        address = ""
        for addr in self.interface:
            if addr.family == socket.AF_PACKET:
                address = addr.address
        if address != "":
            self.mac_address_label.set_label(f"Mac: {address}")
        else:
            self.mac_address_label.set_label("Mac: N/A")

    def on_click(self, user_data):
        if self.is_up:
            self.populate_dropdown()
            self.dropdown.popup()
        return True

    def on_close(self, user_data):
        self.dropdown.clear()
        return True
