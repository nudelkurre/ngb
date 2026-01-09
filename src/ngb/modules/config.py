import os
import json
import tomli
import tomli_w
import yaml
from screeninfo import get_monitors
import psutil


class Config:
    data = dict()
    file_dir = f"{os.environ.get('XDG_CONFIG_HOME', os.path.join(os.environ.get('HOME', ''), '.config'))}/ngb"

    def __init__(self, **kwargs):
        self.file_path = kwargs.get("file_path", f"{self.file_dir}/config.json")
        self.file_type = kwargs.get("file_type", "")
        if self.file_type == "":
            if len(self.file_path.split(".")) < 2:
                print(
                    "File format can not be decided. Please specify file type with --type."
                )
            else:
                self.file_type = self.file_path.split(".")[-1]
        if os.path.isfile(self.file_path):
            self.load_config(self.file_path)
        else:
            self.load_default()

    def load_default(self):
        first_monitor = get_monitors()[0].name
        # Get first first interface after loopback if more than loopback exist
        first_network_interface = (
            list(psutil.net_if_addrs())[1]
            if len(list(psutil.net_if_addrs())) > 1
            else list(psutil.net_if_addrs())[0]
        )
        default_data = {
            "bars": [
                {
                    "output": first_monitor,
                    "widgets": {
                        "left": [{"config": {}, "module": "workspace"}],
                        "center": [],
                        "right": [
                            {"config": {"mountpoint": "/"}, "module": "disk"},
                            {
                                "config": {"interface": first_network_interface},
                                "module": "network",
                            },
                            {"config": {}, "module": "volume"},
                            {
                                "config": {
                                    "timeformat_normal": "%H:%M:%S",
                                    "timeformat_revealer": "%Y-%m-%d",
                                },
                                "module": "clock",
                            },
                        ],
                    },
                }
            ],
            "icon_size": 20,
            "spacing": 5,
            "corner_radius": 0,
        }
        if not os.path.exists(self.file_dir):
            os.makedirs(self.file_dir)
        write_mode = "wb" if self.file_type == "toml" else "w"
        with open(self.file_path, write_mode) as file:
            if self.file_type == "json":
                file.write(json.dumps(default_data))
            elif self.file_type == "toml":
                tomli_w.dump(default_data, file)
            elif self.file_type == "yaml":
                file.write(yaml.dump(default_data))
            file.close()
        self.data = default_data

    def load_config(self, config_file):
        read_mode = "rb" if self.file_type == "toml" else "r"
        with open(config_file, read_mode) as file:
            try:
                if self.file_type == "json":
                    self.data = json.load(file)
                elif self.file_type == "toml":
                    self.data = tomli.load(file)
                elif self.file_type == "yaml":
                    self.data = yaml.safe_load(file)
                if "bars" not in self.data:
                    self.data["bars"] = []
                if "spacing" not in self.data:
                    self.data["spacing"] = 5
                if "icon_size" not in self.data:
                    self.data["icon_size"] = 20
                if "corner_radius" not in self.data:
                    self.data["corner_radius"] = 0
            except json.decoder.JSONDecodeError:
                print("File type is not in valid JSON format")
            except tomli._parser.TOMLDecodeError:
                print("File type is not in valid TOML format")
