import os
import json
from screeninfo import get_monitors
import psutil

class Config:
    data = dict()
    file_path = f"{os.environ['HOME']}/.config/ngb/config"
    file_dir = os.path.dirname(file_path)
    def __init__(self):
        if(os.path.isfile(self.file_path)):
            self.load_config(self.file_path)
        else:
            self.load_default()

    def load_default(self):
        first_monitor = get_monitors()[0].name
        # Get first first interface after loopback if more than loopback exist
        first_network_interface = list(psutil.net_if_addrs())[1] if len(list(psutil.net_if_addrs())) > 1 else list(psutil.net_if_addrs())[0]
        default_data = {
            "bars": [
                {
                    "output": first_monitor,
                    "widgets": {
                        "left": [
                            {
                                "config": {},
                                "module": "workspace"
                            }
                        ],
                        "center": [],
                        "right": [
                            {
                                "config": {
                                    "mountpoint": "/"
                                },
                                "module": "disk"
                            },
                            {
                                "config": {
                                    "interface": first_network_interface
                                },
                                "module": "network"
                            },
                            {
                                "config": {},
                                "module": "volume"
                            },
                            {
                                "config": {
                                    "timeformat_normal": "%H:%M:%S",
                                    "timeformat_revealer": "%Y-%m-%d"
                                },
                                "module": "clock"
                            }
                        ]
                    }
                }
            ],
            "icon_size": 20,
            "spacing": 5
        }
        if(not os.path.exists(self.file_dir)):
            os.makedirs(self.file_dir)
        f = open(self.file_path, "w")
        f.write(json.dumps(default_data))
        f.close()
        self.data = default_data

    def load_config(self, config_file):
        with open(config_file, "r") as file:
            self.data = json.load(file)