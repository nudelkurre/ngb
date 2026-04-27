import psutil
import socket
import requests
from datetime import datetime


class NetworkModule:
    def __init__(self, interface_name):
        self.interface_name = interface_name
        self.public_ip = ""
        self.last_update = 0
        self.first_update = True

    def is_up(self):
        interface_stats = psutil.net_if_stats()[self.interface_name]
        return interface_stats.isup if interface_stats is not None else False

    def get_ipv4_addr(self):
        if self.is_up():
            interface_data = psutil.net_if_addrs()[self.interface_name]
            for address in interface_data:
                if address.family == socket.AddressFamily.AF_INET:
                    return address.address
        return "Not connected"

    def get_ipv6_addrs(self):
        addresses = []
        if self.is_up():
            interface_data = psutil.net_if_addrs()[self.interface_name]
            for address in interface_data:
                if address.family == socket.AddressFamily.AF_INET6:
                    addresses.append(address.address)
        return addresses

    def get_mac_address(self):
        if self.is_up():
            interface_data = psutil.net_if_addrs()[self.interface_name]
            for address in interface_data:
                if address.family == socket.AddressFamily.AF_PACKET:
                    return address.address
        return ""

    def get_public_ip(self):
        try:
            if (
                int(datetime.now().timestamp()) - self.last_update > 300
                or self.first_update
            ):
                req = requests.get("https://ipinfo.io")
                req = req.json()
                self.public_ip = req.get("ip", "0.0.0.0")
                self.first_update = False
                self.last_update = int(datetime.now().timestamp())
            return self.public_ip
        except requests.exceptions.ConnectionError:
            return "Connection error"
        except requests.exceptions.JSONDecodeError:
            return "Could not decode JSON"
