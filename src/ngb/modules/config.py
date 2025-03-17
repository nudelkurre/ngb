import os
import json

class Config:
    data = dict()
    file_path = f"{os.environ['HOME']}/.config/ngb/config"
    def __init__(self):
        if(os.path.isfile(self.file_path)):
            self.load_config(self.file_path)
        else:
            self.load_default()

    def load_default(self):
        default_data = {
            "bars": [
                {
                    "output": "DP-1",
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
                                    "interface": "eth0"
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
        f = open(self.file_path, "w")
        f.write(json.dumps(default_data))
        f.close()
        self.data = default_data

    def load_config(self, config_file):
        with open(config_file, "r") as file:
            self.data = json.load(file)