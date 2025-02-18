from gi.repository import Gtk
from gi.repository import GLib
import psutil
import socket

from pybar.modules import WidgetBox

class Network(WidgetBox):
    interface = []
    ipv4_addr = Gtk.Label()
    ipv6_addr = Gtk.Label()
    text_label = Gtk.Label()
    icon_label = Gtk.Label()

    def __init__(self, interface):
        self.interface = psutil.net_if_addrs()[interface]
        WidgetBox.__init__(self, icon="󰈀", timer=10000)

    def set_text(self):
        self.get_ipv4_addr()
        return True

    def get_ipv4_addr(self):
        address= ""
        for addr in self.interface:
            if(addr.family == socket.AF_INET and address == ""):
                address = addr.address
        self.text_label.set_label(address)
        return True

    def get_ipv6_addrs(self):
        addrs: list = []
        for addr in self.interface:
            if(addr.family == socket.AF_INET6):
                addrs.append(addr.address)
        return addrs