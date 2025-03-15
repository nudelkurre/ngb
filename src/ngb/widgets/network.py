from gi.repository import Gtk
from gi.repository import GLib
import psutil
import socket

from ngb.modules import WidgetBox

class Network(WidgetBox):
    interface = []
    
    def __init__(self, **kwargs):
        self.interface = psutil.net_if_addrs()[kwargs.get("interface", "")]
        self.timer = kwargs.get("timer", 10)
        self.icon = kwargs.get("icon", "󰈀")
        self.icon_size = kwargs.get("icon_size", 20)
        super().__init__(icon=self.icon, timer=self.timer, icon_size=self.icon_size)

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