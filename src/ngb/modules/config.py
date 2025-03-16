import os
import yaml

class Config:
    data = dict()
    def __init__(self):
        if(os.path.isfile(f"{os.environ['HOME']}/.config/ngb/config")):
            self.load_config(f"{os.environ['HOME']}/.config/ngb/config")
        else:
            self.load_default()

    def load_default(self):
        default_data = """
        bars:
        - output: DP-1
          widgets:
            left:
            - workspace
            center: []
            right:
            - config:
                mountpoint: /
                module: disk
            - config:
                interface: eth0
                module: network
            - config: {}
              module: volume
            - config:
                timeformat_normal: '%H:%M:%S'
                timeformat_revealer: '%Y-%m-%d %H:%M:%S'
                module: clock
        icon_size: 20
        """
        self.data = yaml.safe_load(default_data)

    def load_config(self, config_file):
        with open(config_file, "r") as file:
            self.data = yaml.safe_load(file)