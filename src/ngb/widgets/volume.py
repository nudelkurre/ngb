from gi.repository import Gtk
from gi.repository import GLib
from shutil import which

import subprocess
import re

from ngb.modules import WidgetBox

class Volume(WidgetBox):
    path = which("wpctl")
    def __init__(self, **kwargs):
        self.icon = kwargs.get("icon", "")
        self.timer = kwargs.get("timer", 0.2)
        self.icon_size = kwargs.get("icon_size", 20)
        self.click_to_mute = kwargs.get("click_to_mute", False)
        self.sinks = []
        super().__init__(icon=self.icon, timer=self.timer, icon_size=self.icon_size)
        self.get_sinks()
        self.populate_dropdown()
        self.update_sinks()

    def get_volume(self, sink):
        if(self.path):
            volume = subprocess.run(f"wpctl get-volume {sink}".split(), capture_output=True, text=True).stdout
            volume = volume.split(" ")
            if(len(volume) == 2): 
                volume = float(volume[1].lstrip().rstrip()) * 100
                volume = f"{int(volume)}%"
                self.text_label.set_label(volume)
            elif(len(volume) == 3 and "MUTED" in volume[2]):
                self.text_label.set_label("Muted")
        else:
            self.text_label.set_label("wpctl is not installed")
            self.icon_label.set_visible(False)
        return True

    def get_sinks(self):
        new_sinks = []
        new_sink_names = []
        old_sink_names = []
        if(self.path):
            for i in self.sinks:
                old_sink_names.append(i["name"])
            wpctl = subprocess.run("wpctl status".split(), capture_output=True, text=True).stdout#.split("\n\n")

            sinks = re.search(r"Audio\n([\W\w]*)Video", wpctl).group(1)
            sinks = re.search(r"Sinks:\n([\W\w]*)Sources", sinks).group(1).split("\n")[:-2]

            for i in sinks:
                match = re.search(r"\s*(?P<default>\*?)\s*(?P<id>\d+)\.\s*(?P<name>[\w\s\d\[\]\(\)-\/]+)\s*\[vol:\s*(?P<volume>\d+\.\d+)\s?(?P<muted>MUTED)*\]", i)
                if(match):
                    sink = {"id": match.group("id"),
                        "name": match.group("name").lstrip().rstrip(),
                        "volume": int(float(match.group("volume")) * 100),
                        "muted": True if match.group("muted") == "MUTED" else False,
                        "default": True if match.group("default") == "*" else False
                    }
                    new_sinks.append(sink)
                    new_sink_names.append(sink["name"])
            if(new_sink_names != old_sink_names):
                self.sinks = new_sinks
                self.populate_dropdown()
        return True

    def set_volume(self, sink, volume):
        if(self.path):
            volume_cmd = f"wpctl set-volume {sink} {volume}".split()
            subprocess.run(volume_cmd)

    def toggle_mute(self, sink):
        if(self.path):
            subprocess.run(f"wpctl set-mute {sink} toggle".split())

    def change_default_sink(self):
        self.get_sinks()
        if(len(self.sinks) > 0):
            default = 0
            for index, sink in enumerate(self.sinks):
                if(sink["default"]):
                    default = index
        
        self.set_default_sink(self.sinks[(default + 1) % len(self.sinks)]['id'])
    
    def set_default_sink(self, sink):
        subprocess.run(f"wpctl set-default {sink}".split())

    def populate_dropdown(self):
        self.dropdown.clear()
        for sink in self.sinks:
            sink_label = Gtk.Label()
            # Split string to insert new line at every 25 character
            # to line wrap long sink names
            sink_text = "\n".join(re.findall(".{1,25}", sink["name"]))
            sink_label.set_label(sink_text)
            self.dropdown.add(sink_label)
            slider_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=self.spacing)
            slider = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL)
            slider.set_range(0, 100)
            slider.set_digits(0)
            slider.set_draw_value(True)
            slider.set_value_pos(Gtk.PositionType.RIGHT)
            slider.set_value(sink["volume"])
            slider.set_name(sink["id"])
            slider.connect("value-changed", self.on_slider_change)
            slider_box.append(slider)
            self.dropdown.add(slider_box)
        return True

    def set_text(self):
        self.get_volume("@DEFAULT_AUDIO_SINK@")
        return True

    def on_slider_change(self, scale):
        volume = scale.get_value() / 100
        self.set_volume(scale.get_name(), volume)

    def on_scroll(self, controller, x, y):
        if(y < 0):
            self.set_volume("@DEFAULT_AUDIO_SINK@", "5%+")
        elif(y > 0):
            self.set_volume("@DEFAULT_AUDIO_SINK@", "5%-")

    def on_click(self, user_data):
        if(self.click_to_mute):
            self.toggle_mute("@DEFAULT_AUDIO_SINK@")
        else:
            self.dropdown.popup()

    def on_middle_click(self, sequence, user_data):
        if(not self.click_to_mute):
            self.toggle_mute("@DEFAULT_AUDIO_SINK@")
        else:
            self.dropdown.popup()

    def on_right_click(self, sequence, user_data):
        self.change_default_sink()

    def update_sinks(self):
        GLib.timeout_add(1000, self.get_sinks)