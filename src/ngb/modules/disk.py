import psutil
from psutil._common import bytes2human

from .namedtuples import NamedTuples

DiskInfo = NamedTuples.DiskInfo


class DiskModule:
    def __init__(self, mountpoint="/"):
        self.mountpoint = mountpoint

    def get_disk_usage(self):
        disk = psutil.disk_usage(self.mountpoint)
        return DiskInfo(
            percentage=f"{disk.percent}%",
            used=f"{bytes2human(disk.used)}iB",
            total=f"{bytes2human(disk.total)}iB",
        )

    def get_used_fraction(self):
        disk = psutil.disk_usage(self.mountpoint)
        return disk.used / disk.total
