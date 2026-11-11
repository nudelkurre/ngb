import os
import json
import tomli
import tomli_w
import yaml


class ConfigError(Exception):
    pass


class ValidateConfig:
    valid_config_keys = {
        "bars": list,
        "corner_radius": int,
        "font_size": int,
        "gaps": int,
        "height": int,
        "icon_size": int,
        "layer": str,
        "spacing": int,
    }

    valid_bar_settings = {
        "gaps": int,
        "height": int,
        "layer": str,
        "location": str,
        "output": str,
        "widgets": dict,
    }

    valid_widgets = {
        "battery": {
            "icon_size": int,
            "spacing": int,
            "timer": int,
        },
        "bluetooth": {
            "icon_size": int,
            "spacing": int,
            "timer": int,
        },
        "clock": {
            "timeformat_normal": str,
            "timeformat_revealer": str,
            "show_heading": bool,
            "show_day_names": bool,
            "show_week_numbers": bool,
            "show_revealer": bool,
            "icon_size": int,
            "spacing": int,
            "timer": int,
        },
        "cpu": {
            "icon_size": int,
            "spacing": int,
            "timer": int,
        },
        "disk": {
            "mountpoint": str,
            "icon": str,
            "icon_size": int,
            "spacing": int,
            "timer": int,
        },
        "headset": {
            "icon_size": int,
            "spacing": int,
            "timer": int,
        },
        "keymode": {
            "icon_size": int,
            "spacing": int,
            "timer": int,
            "keymode_icons": dict,
        },
        "network": {
            "interface": str,
            "show_public_ip": bool,
            "show_ipv6": bool,
            "show_disconnected": bool,
            "icon_size": int,
            "icon": str,
            "spacing": int,
            "timer": int,
        },
        "volume": {
            "click_to_mute": bool,
            "muted_icon": str,
            "unmuted_icon": str,
            "icon_size": int,
            "spacing": int,
            "timer": int,
        },
        "weather": {
            "city": str,
            "api": str,
            "show_big_icon": bool,
            "big_icon_size": int,
            "small_text_size": int,
            "icon_size": int,
            "spacing": int,
            "timer": int,
        },
        "windowtitle": {
            "hide_no_focus": bool,
            "hide_on_close": bool,
            "title_max_length": int,
            "icon_size": int,
            "spacing": int,
            "timer": int,
        },
        "workspace": {
            "icon_size": int,
            "monitor": str,
            "use_workspace_names": bool,
            "use_workspace_ids": bool,
            "default_name": str,
            "names": dict,
            "icon_size": int,
            "spacing": int,
            "timer": int,
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
                        elif not isinstance(bar.get(bc).get(bcl), list):
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
                        widget.get([*widget][0], {}).get(setting),
                        self.valid_widgets.get([*widget][0], {}).get(setting),
                    ):
                        raise ConfigError(
                            f"{setting} should be {self.valid_widgets.get([*widget][0], {}).get(setting).__name__} but are {type(setting)}"
                        )
