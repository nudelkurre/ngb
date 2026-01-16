from gi.repository import Gtk
from gi.repository import GLib
from shutil import which

import subprocess
import re

from ngb.modules import NamedTuples, WidgetBox

VolumeSink = NamedTuples.VolumeSink


class MuteButton(Gtk.Button):
    def __init__(self, **kwargs):
        super().__init__()
        self.id = kwargs.get("id")
        self.path = kwargs.get("path")
        self.icon_size = kwargs.get("icon_size", 20)
        self.muted_icon = kwargs.get("muted_icon", "󰝟")
        self.unmuted_icon = kwargs.get("unmuted_icon", "󰕾")
        self.mute_label = Gtk.Label()
        self.mute_label.set_markup(self.get_muted())
        self.set_child(self.mute_label)
        self.connect("clicked", self.on_mute)

    def get_sink(self):
        cmd = f"wpctl status"
        wpctl = subprocess.run(cmd.split(), capture_output=True, text=True).stdout
        muted = re.search(
            rf"(?P<id>{self.id})\.\s(?P<name>[\w\s]+)\[vol:\s(?P<volume>\d+\.\d+)\s?(?P<muted>MUTED)?\]",
            wpctl,
        )
        sink = VolumeSink(
            id=muted.group("id"),
            name=muted.group("name").lstrip().rstrip(),
            volume=float(muted.group("volume")),
            muted=True if muted.group("muted") == "MUTED" else False,
        )
        return sink

    def on_mute(self, user_data):
        self.toggle_mute()
        self.mute_label.set_markup(self.get_muted())

    def toggle_mute(self):
        if self.path:
            subprocess.run(f"wpctl set-mute {self.id} toggle".split())

    def get_muted(self):
        sink = self.get_sink()
        if sink.muted:
            return f'<span font="{self.icon_size}">{self.muted_icon}</span>'
        else:
            return f'<span font="{self.icon_size}">{self.unmuted_icon}</span>'


class Volume(WidgetBox):
    path = which("wpctl")

    def __init__(self, **kwargs):
        self.icon = kwargs.get("icon", "")
        self.timer = kwargs.get("timer", 5)
        self.icon_size = kwargs.get("icon_size", 20)
        self.click_to_mute = kwargs.get("click_to_mute", False)
        self.muted_icon = kwargs.get("muted_icon", "󰝟")
        self.unmuted_icon = kwargs.get("unmuted_icon", "󰕾")
        self.sinks = []
        super().__init__(icon=self.icon, timer=self.timer, icon_size=self.icon_size)

    def run(self):
        self.set_icon()
        self.set_text()
        self.update_label()
        self.get_sinks()

        # Connect signals for dropdown
        self.dropdown.connect("show", self.on_show)
        self.dropdown.connect("closed", self.on_close)

    def get_volume(self, sink):
        if self.path:
            volume = subprocess.run(
                f"wpctl get-volume {sink}".split(), capture_output=True, text=True
            ).stdout
            volume = volume.split(" ")
            if len(volume) == 2:
                volume = float(volume[1].lstrip().rstrip()) * 100
                volume = f"{int(volume)}%"
                self.text_label.set_label(volume)
            elif len(volume) == 3 and "MUTED" in volume[2]:
                self.text_label.set_label("Muted")
        else:
            self.text_label.set_label("wpctl is not installed")
            self.icon_label.set_visible(False)
        return True

    def get_sinks(self):
        new_sinks = []
        new_sink_names = []
        old_sink_names = []
        new_default = 0
        old_default = 0
        if self.path:
            for i in self.sinks:
                old_sink_names.append(i.get("name", ""))
                if i.get("default"):
                    old_default = i.get("id")
            # Get output from wpctl
            wpctl = subprocess.run(
                "wpctl status".split(), capture_output=True, text=True
            ).stdout

            # Get only parts that are in the Audio section of wpctl output
            sinks = re.search(r"Audio\n([\W\w]*)Video", wpctl).group(1)
            # Get only audio sinks
            sinks = (
                re.search(r"Sinks:\n([\W\w]*)Sources", sinks).group(1).split("\n")[:-2]
            )

            for i in sinks:
                # Search each sink for id, name, volume, if muted and if default
                match = re.search(
                    r"\s*(?P<default>\*?)\s*(?P<id>\d+)\.\s*(?P<name>[\w\s\d\[\]\(\)-\/]+)\s*\[vol:\s*(?P<volume>\d+\.\d+)\s?(?P<muted>MUTED)*\]",
                    i,
                )
                if match:
                    sink = {
                        "id": match.group("id"),
                        "name": match.group("name").lstrip().rstrip(),
                        "volume": int(float(match.group("volume")) * 100),
                        "muted": True if match.group("muted") == "MUTED" else False,
                        "default": True if match.group("default") == "*" else False,
                    }
                    new_sinks.append(sink)
                    new_sink_names.append(sink.get("name"))
                    if sink.get("default"):
                        new_default = sink.get("id")
            self.sinks = new_sinks
        return True

    def set_volume(self, sink, volume):
        if self.path:
            volume_cmd = f"wpctl set-volume {sink} {volume}".split()
            subprocess.run(volume_cmd)

    def toggle_mute(self, sink):
        if self.path:
            subprocess.run(f"wpctl set-mute {sink} toggle".split())

    def change_default_sink(self):
        default = self.get_default_sink()
        # Set the new default sink by move to next id in sink list
        # or to first if current is last
        self.set_default_sink(self.sinks[(default + 1) % len(self.sinks)].get("id"))

    def get_default_sink(self):
        self.get_sinks()
        if len(self.sinks) > 0:
            default = 0
            # Iterate the sink list and if sink is default get index of deafult sink
            for index, sink in enumerate(self.sinks):
                if sink.get("default"):
                    default = index
        return default

    def set_default_sink(self, sink):
        subprocess.run(f"wpctl set-default {sink}".split())

    def populate_dropdown(self):
        self.get_sinks()
        for sink in self.sinks:
            sink_label = Gtk.Label()
            # Split string to insert new line at every 25 character
            # to line wrap long sink names
            sink_text = "\n".join(re.findall(".{1,25}", sink.get("name")))
            sink_label.set_label(sink_text)
            self.dropdown.add(sink_label)
            slider_box = Gtk.Box(
                orientation=Gtk.Orientation.HORIZONTAL, spacing=self.spacing
            )
            slider = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL)
            slider.set_range(0, 100)
            slider.set_digits(0)
            slider.set_draw_value(True)
            slider.set_value_pos(Gtk.PositionType.RIGHT)
            slider.set_value(sink["volume"])
            slider.set_name(sink["id"])
            slider.connect("value-changed", self.on_slider_change)
            slider_box.append(slider)
            mute_button = MuteButton(
                icon_size=self.icon_size,
                path=self.path,
                id=sink["id"],
                muted_icon=self.muted_icon,
                unmuted_icon=self.unmuted_icon,
            )
            slider_box.append(mute_button)
            self.dropdown.add(slider_box)
        return True

    def set_text(self):
        self.get_volume("@DEFAULT_AUDIO_SINK@")
        return True

    def on_slider_change(self, scale):
        volume = scale.get_value() / 100
        self.set_volume(scale.get_name(), volume)
        # Only update label if slider change is for default sink
        if scale.get_name() == self.sinks[self.get_default_sink()].get("id"):
            self.set_text()

    def on_scroll(self, controller, x, y):
        if y < 0:
            self.set_volume("@DEFAULT_AUDIO_SINK@", "5%+")
            self.set_text()
        elif y > 0:
            self.set_volume("@DEFAULT_AUDIO_SINK@", "5%-")
            self.set_text()

    def on_click(self, user_data):
        if self.click_to_mute:
            self.toggle_mute("@DEFAULT_AUDIO_SINK@")
        else:
            self.dropdown.popup()

    def on_middle_click(self, sequence, user_data):
        if not self.click_to_mute:
            self.toggle_mute("@DEFAULT_AUDIO_SINK@")
        else:
            self.dropdown.popup()

    def on_right_click(self, sequence, user_data):
        self.change_default_sink()

    def on_show(self, user_data):
        self.populate_dropdown()

    def on_close(self, user_data):
        self.dropdown.clear()

    def on_mute(self, user_data, mute_button_label):
        # print(user_data, mute_button_label)
        if mute_button_label.get_label() == "Mute":
            mute_button_label.set_label("Muted")
        elif mute_button_label.get_label() == "Muted":
            mute_button_label.set_label("Mute")

    def update_sinks(self):
        GLib.timeout_add(1000, self.get_sinks)
