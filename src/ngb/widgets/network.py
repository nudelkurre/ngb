from gi.repository import Gtk
from gi.repository import GLib
import psutil
import socket

from ngb.modules import WidgetBox

class Network(WidgetBox):
    interface = []
    
    def __init__(self, **kwargs):
        self.interface_name = kwargs.get("interface", "")
        self.interface = psutil.net_if_addrs()[self.interface_name] if self.interface_name in psutil.net_if_addrs() else []
        self.timer = kwargs.get("timer", 10)
        self.icon = kwargs.get("icon", "󰈀")
        self.icon_size = kwargs.get("icon_size", 20)
        self.interface_label = Gtk.Label(label=f"Interface: {self.interface_name}")
        self.ipv4_header_label = Gtk.Label(label="IPv4:")
        self.ipv6_header_label = Gtk.Label(label="IPv6:")
        self.ipv4_label = Gtk.Label()
        self.ipv4_label.set_justify(Gtk.Justification.CENTER)
        self.ipv6_label = Gtk.Label()
        self.ipv6_label.set_justify(Gtk.Justification.CENTER)
        self.ipv6_label.add_css_class("multi-line")
        self.mac_address_label = Gtk.Label()
        super().__init__(icon=self.icon, timer=self.timer, icon_size=self.icon_size)
        self.populate_dropdown()

    def set_text(self):
        self.get_ipv4_addr()
        self.get_ipv6_addrs()
        self.get_mac_address()
        return True

    def populate_dropdown(self):
        self.dropdown.add(self.interface_label)
        self.dropdown.add(self.mac_address_label)
        self.dropdown.add(self.ipv4_header_label)
        self.dropdown.add(self.ipv4_label)
        self.dropdown.add(self.ipv6_header_label)
        self.dropdown.add(self.ipv6_label)

    def get_ipv4_addr(self):
        address = ""
        for addr in self.interface:
            if(addr.family == socket.AF_INET and address == ""):
                address = addr.address
        if(address != ""):
            self.text_label.set_label(address)
            self.ipv4_label.set_label(address)
            self.ipv4_label.set_visible(True)
            self.ipv4_header_label.set_visible(True)
        else:
            self.text_label.set_label("N/A")
            self.ipv4_label.set_visible(False)
            self.ipv4_header_label.set_visible(False)
        return True

    def get_ipv6_addrs(self):
        addrs = []
        for addr in self.interface:
            if(addr.family == socket.AF_INET6):
                addrs.append(addr.address)
        if(len(addrs) > 0):
            self.ipv6_label.set_label("\n".join(addrs))
            self.ipv6_label.set_visible(True)
            self.ipv6_header_label.set_visible(True)
        else:
            self.ipv6_label.set_visible(False)
            self.ipv6_header_label.set_visible(False)
        return True

    def get_mac_address(self):
        address = ""
        for addr in self.interface:
            if(addr.family == socket.AF_PACKET):
                address = addr.address
        if(address != ""):
            self.mac_address_label.set_label(f"Mac: {address}")
        else:
            self.mac_address_label.set_label("Mac: N/A")

    def on_click(self, user_data):
        self.dropdown.popup()
        return True