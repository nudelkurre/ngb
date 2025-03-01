from gi.repository import Gtk
from gi.repository import GLib
import subprocess
import re

from ngb.modules import WidgetBox

class Volume(WidgetBox):
    def __init__(self):
        super().__init__(icon="", timer=200)

    def get_volume(self):
        volume = subprocess.run("wpctl get-volume @DEFAULT_AUDIO_SINK@".split(), capture_output=True, text=True).stdout
        volume = volume.split(" ")
        if(len(volume) == 2): 
            volume = float(volume[1].lstrip().rstrip()) * 100
            volume = f"{int(volume)}%"
            self.text_label.set_label(volume)
        elif(len(volume) == 3 and "MUTED" in volume[2]):
            self.text_label.set_label("Muted")
        return True

    def set_text(self):
        self.get_volume()
        return True

    def on_scroll(self, controller, x, y):
        volume_cmd = "wpctl set-volume @DEFAULT_AUDIO_SINK@"
        if(y < 0):
            volume_cmd = f"{volume_cmd} 5%+".split()
            subprocess.run(volume_cmd)
        elif(y > 0):
            volume_cmd = f"{volume_cmd} 5%-".split()
            subprocess.run(volume_cmd)

    def on_click(self, sequence, user_data):
        subprocess.run("wpctl set-mute @DEFAULT_AUDIO_SINK@ toggle".split())

    def on_right_click(self, sequence, user_data):
        wpctl = subprocess.run("wpctl status".split(), capture_output=True, text=True).stdout#.split("\n\n")

        sinks = re.search(r"Audio\n([\W\w]*)Video", wpctl).group(1)
        sinks = re.search(r"Sinks:\n([\W\w]*)Sources", sinks).group(1).split("\n")[:-2]
        sink_list = []

        for i in sinks:
            match = re.search(r"\s*(\*?)\s*(\d+)\.\s*([\w\s\d]+)\s*\[vol:\s*(\d+\.\d+)\]", i)
            if(match):
                sink = {"id": match.group(2),
                    "name": match.group(3).lstrip().rstrip(),
                    "volume": int(float(match.group(4)) * 100),
                    "default": True if match.group(1) == "*" else False
                }
                sink_list.append(sink)

        default = 0
        for index, sink in enumerate(sink_list):
            if(sink["default"]):
                default = index
        
        subprocess.run(f"wpctl set-default {sink_list[(default + 1) % len(sink_list)]['id']}".split())