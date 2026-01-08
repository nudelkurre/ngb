#!/usr/bin/env python3
from ctypes import CDLL

CDLL("libgtk4-layer-shell.so")

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Gtk4LayerShell", "1.0")
gi.require_version("Gdk", "4.0")

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Gio
from gi.repository import GLib

import sys
import uuid

from ngb.widgets import (
    Battery,
    Bluetooth,
    Clock,
    Cpu,
    Disk,
    Headset,
    Network,
    Volume,
    Weather,
    Workspaces,
)
from ngb.modules import Bar, Config
from ngb import __about__


class MainWindow(Gtk.Application):
    def __init__(self):
        app_id = f"com.github.nudelkurre.ngb-{uuid.uuid4()}"
        super().__init__(
            application_id=app_id,
            flags=Gio.ApplicationFlags.FLAGS_NONE
            | Gio.ApplicationFlags.HANDLES_COMMAND_LINE,
        )
        self.config_file_path = ""
        self.config_file_type = ""
        self.add_main_option(
            "version",
            ord("v"),
            GLib.OptionFlags.NONE,
            GLib.OptionArg.NONE,
            "Show application version",
            None,
        )
        self.add_main_option(
            "config",
            ord("c"),
            GLib.OptionFlags.IN_MAIN,
            GLib.OptionArg.STRING,
            "Specify path to config file",
            None,
        )
        self.add_main_option(
            "type",
            ord("t"),
            GLib.OptionFlags.IN_MAIN,
            GLib.OptionArg.STRING,
            "Specify file type for config file (suppported are json, toml, yaml)",
            None,
        )

    def do_activate(self):
        if self.config_file_path:
            self.config = Config(
                file_path=self.config_file_path, file_type=self.config_file_type
            )
        else:
            self.config = Config()
        self.load_css()
        for i in self.config.data.get("bars", {}):
            self.create_window(i)

    def create_window(self, bar_config):
        local_bar_config = {}
        local_bar_config["monitor"] = bar_config.get("output", "")
        if "gaps" in bar_config:
            local_bar_config["gaps"] = bar_config.get("gaps", 0)
        elif "gaps" in self.config.data:
            local_bar_config["gaps"] = self.config.data.get("gaps", 0)
        if "location" in bar_config:
            local_bar_config["location"] = bar_config.get("location", "top")
        if "height" in bar_config:
            local_bar_config["height"] = bar_config.get("height", 25)
        elif "height" in self.config.data:
            local_bar_config["height"] = self.config.data.get("height", 25)
        if "layer" in bar_config:
            local_bar_config["layer"] = bar_config.get("layer", "bottom")
        elif "layer" in self.config.data:
            local_bar_config["layer"] = self.config.data.get("layer", "bottom")
        window = Bar(app=self, **local_bar_config)
        window.show()

        valid_widgets = {
            "battery": Battery,
            "bluetooth": Bluetooth,
            "clock": Clock,
            "cpu": Cpu,
            "disk": Disk,
            "headset": Headset,
            "network": Network,
            "volume": Volume,
            "weather": Weather,
            "workspace": Workspaces,
        }

        for widget in bar_config.get("widgets", {}).get("left", {}):
            config = widget.get("config", {})
            if "icon_size" not in config and "icon_size" in self.config.data:
                config["icon_size"] = self.config.data.get("icon_size", 20)
            module = widget.get("module", [])
            if module in valid_widgets:
                new_module = valid_widgets.get(module)(**config)
                window.left(new_module)
                new_module.run()

        for widget in bar_config["widgets"]["center"]:
            config = widget["config"]
            if "icon_size" not in config and "icon_size" in self.config.data:
                config["icon_size"] = self.config.data.get("icon_size", 20)
            module = widget.get("module", [])
            if module in valid_widgets:
                new_module = valid_widgets.get(module)(**config)
                window.center(new_module)
                new_module.run()

        for widget in bar_config["widgets"]["right"]:
            config = widget["config"]
            if "icon_size" not in config and "icon_size" in self.config.data:
                config["icon_size"] = self.config.data.get("icon_size", 20)
            module = widget.get("module", [])
            if module in valid_widgets:
                new_module = valid_widgets.get(module)(**config)
                window.right(new_module)
                new_module.run()

    def load_css(self):
        css_provider = Gtk.CssProvider()
        css = f"""
        .widget-button {{
            background-color: transparent;
            border: none;
            padding: 0 {self.config.data.get("spacing", 0)}px;
            outline: none;
        }}

        .widget-button:active {{
            background-color: transparent;
        }}

        .multi-line {{
            line-height: 1.6;
        }}

        .widget-box {{
            margin: 0 {self.config.data.get("spacing", 0)}px;
        }}

        scale {{
            min-width: 200px;
        }}

        .dropdown {{
            padding: 10px 0;
        }}

        window {{
            border-radius: {self.config.data.get("corner_radius", 0)}px;
        }}
        """
        css_provider.load_from_data(css.encode("utf-8"))

        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(), css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER
        )

    def do_command_line(self, command_line):
        options = command_line.get_options_dict()
        options = options.end().unpack()
        if "version" in options:
            print(f"Version: {__about__.__version__}")
        else:
            if "config" in options:
                self.config_file_path = options["config"]
            if "type" in options:
                self.config_file_type = options["type"]
            self.activate()
        return True


def main():
    try:
        app = MainWindow()
        app.run(sys.argv)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
