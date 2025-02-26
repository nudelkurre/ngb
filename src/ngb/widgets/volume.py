from gi.repository import Gtk
from gi.repository import GLib
import subprocess

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

    def on_click(self, controller, n_press, x, y):
        subprocess.run("wpctl set-mute @DEFAULT_AUDIO_SINK@ toggle".split())