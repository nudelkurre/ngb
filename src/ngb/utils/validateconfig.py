import os
import json
import tomli
import tomli_w
import yaml


class ConfigError(Exception):
    pass


class ValidateConfig:
    valid_config_keys = {
        "bars": type(list()),
        "corner_radius": type(int()),
        "font_size": type(int()),
        "gaps": type(int()),
        "height": type(int()),
        "icon_size": type(int()),
        "spacing": type(int()),
    }

    valid_bar_settings = {
        "gaps": type(int()),
        "height": type(int()),
        "layer": type(str()),
        "location": type(str()),
        "output": type(str()),
        "widgets": type(dict()),
    }

    valid_widgets = {
        "battery": {
            "icon_size": type(int()),
            "spacing": type(int()),
            "timer": type(int()),
        },
        "bluetooth": {
            "icon_size": type(int()),
            "spacing": type(int()),
            "timer": type(int()),
        },
        "clock": {
            "timeformat_normal": type(str()),
            "timeformat_revealer": type(str()),
            "show_heading": type(bool()),
            "show_day_names": type(bool()),
            "show_week_numbers": type(bool()),
            "icon_size": type(int()),
            "spacing": type(int()),
            "timer": type(int()),
        },
        "cpu": {
            "icon_size": type(int()),
            "spacing": type(int()),
            "timer": type(int()),
        },
        "disk": {
            "mountpoint": type(str()),
            "icon_size": type(int()),
            "spacing": type(int()),
            "timer": type(int()),
        },
        "headset": {
            "icon_size": type(int()),
            "spacing": type(int()),
            "timer": type(int()),
        },
        "network": {
            "interface": type(str()),
            "show_public_ip": type(bool()),
            "show_ipv6": type(bool()),
            "show_disconnected": type(bool()),
            "icon_size": type(int()),
            "spacing": type(int()),
            "timer": type(int()),
        },
        "volume": {
            "click_to_mute": type(bool()),
            "muted_icon": type(str()),
            "unmuted_icon": type(str()),
            "icon_size": type(int()),
            "spacing": type(int()),
            "timer": type(int()),
        },
        "weather": {
            "city": type(str()),
            "api": type(str()),
            "show_big_icon": type(bool()),
            "big_icon_size": type(int()),
            "icon_size": type(int()),
            "spacing": type(int()),
            "timer": type(int()),
        },
        "window_title": {
            "hide_no_focus": type(bool()),
            "hide_on_close": type(bool()),
            "title_max_length": type(int()),
            "icon_size": type(int()),
            "spacing": type(int()),
            "timer": type(int()),
        },
        "workspace": {
            "icon_size": type(int()),
            "monitor": type(str()),
            "use_workspace_names": type(bool()),
            "use_workspace_ids": type(bool()),
            "default_name": type(str()),
            "names": type(dict()),
            "icon_size": type(int()),
            "spacing": type(int()),
            "timer": type(int()),
        },
    }

    def __init__(self, **kwargs):
        self.file_path = kwargs.get("file_path")
        self.file_type = kwargs.get("file_type")
        self.config = {}
        self.load_config()
        self.validate_root()
        self.validate_bars()

    # Load the config file
    def load_config(self):
        if self.file_type == "":
            if len(self.file_path.split(".")) < 2:
                print(
                    "File format can not be decided. Please specify file type with --type."
                )
            else:
                self.file_type = self.file_path.split(".")[-1]
        if os.path.isfile(self.file_path):
            read_mode = "rb" if self.file_type == "toml" else "r"
            with open(self.file_path, read_mode) as file:
                try:
                    match self.file_type:
                        case "json":
                            self.config = json.load(file)
                        case "toml":
                            self.config = tomli.load(file)
                        case "yaml":
                            self.config = yaml.safe_load(file)
                    if "bars" not in self.config:
                        self.config["bars"] = []
                    if "spacing" not in self.config:
                        self.config["spacing"] = 5
                    if "icon_size" not in self.config:
                        self.config["icon_size"] = 20
                    if "corner_radius" not in self.config:
                        self.config["corner_radius"] = 0
                except json.decoder.JSONDecodeError:
                    print("File type is not in valid JSON format")
                except tomli._parser.TOMLDecodeError:
                    print("File type is not in valid TOML format")
        else:
            raise ConfigError(f"{self.file_path} does not exist")

    # Validate the global settings for ngb
    def validate_root(self):
        root_keys = [*self.config]
        for key in root_keys:
            if key not in self.valid_config_keys:
                raise ConfigError(f"{key} invalid global setting")
            else:
                if not isinstance(
                    self.config.get(key), self.valid_config_keys.get(key)
                ):
                    raise ConfigError(
                        f"{key} is wrong type, should be {self.valid_config_keys.get(key).__name__}"
                    )

    # Validate each bar
    def validate_bars(self):
        bars = [*self.config.get("bars", {})]
        for bar in bars:
            for bc in [*bar]:
                if bc not in [*self.valid_bar_settings]:
                    raise ConfigError(f"{bc} is invalid bar setting for {bar}")
                if bc == "widgets":
                    for bcl in [*bar.get(bc)]:
                        if bcl not in ["left", "center", "right"]:
                            raise ConfigError(f"Widget location {bcl} invalid")
                        elif not isinstance(bar.get(bc).get(bcl), type(list())):
                            raise ConfigError(f"{bcl} is not a list")
                        self.validate_widgets(
                            bar.get("output", ""), bar.get(bc).get(bcl)
                        )

    # Validate each widget for the bar
    def validate_widgets(self, output, widgets):
        for widget in widgets:
            if len([*widget]) > 1:
                raise ConfigError(f"Widget configured incorrectly")
            elif [*widget][0] not in self.valid_widgets:
                raise ConfigError(f"{[*widget][0]} is an invalid widget")
            else:
                for setting in widget.get([*widget][0]):
                    if setting not in self.valid_widgets.get([*widget][0], {}):
                        raise ConfigError(
                            f"{setting} is invalid setting for {[*widget][0]}"
                        )
                    elif not isinstance(
                        setting, self.valid_widgets.get([*widget][0], {}).get(setting)
                    ):
                        raise ConfigError(
                            f"{setting} should be {self.valid_widgets.get([*widget][0], {}).get(setting).__name__}"
                        )
