from gi.repository import Gtk
from gi.repository import GLib
import psutil
import socket

class Network(Gtk.Box):
    interface: list
    ipv4_addr = Gtk.Label()
    ipv6_addr = Gtk.Label()


    def __init__(self, interface):
        self.interface = psutil.net_if_addrs()[interface]
        Gtk.Box.__init__(self)
        self.append(self.ipv4_addr)
        self.get_ipv4_addr()
        self.check_update_address()

    def get_ipv4_addr(self):
        address= ""
        for addr in self.interface:
            if(addr.family == socket.AF_INET and address == ""):
                address = addr.address
        self.ipv4_addr.set_label(address)
        return True

    def get_ipv6_addrs(self):
        addrs: list = []
        for addr in self.interface:
            if(addr.family == socket.AF_INET6):
                addrs.append(addr.address)
        return addrs

    def check_update_address(self):
        GLib.timeout_add(10000, self.get_ipv4_addr)