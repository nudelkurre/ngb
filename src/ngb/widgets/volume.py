from gi.repository import Gtk
from gi.repository import GLib
import re

from ngb.modules import VolumeModule, WidgetBox


class MuteButton(Gtk.Button):
    def __init__(self, **kwargs):
        super().__init__()
        self.sink = kwargs.get("sink")
        self.icon_size = kwargs.get("icon_size", 20)
        self.muted_icon = kwargs.get("muted_icon", "󰝟")
        self.unmuted_icon = kwargs.get("unmuted_icon", "󰕾")
        self.volume = kwargs.get("volume_module")
        self.mute_label = Gtk.Label()
        self.mute_label.add_css_class("icon")
        self.mute_label.set_label(self.get_muted())
        self.set_child(self.mute_label)
        self.connect("clicked", self.on_mute)

    def on_mute(self, user_data):
        self.volume.toggle_mute(self.sink.id)
        self.sink = self.sink._replace(muted=not self.sink.muted)
        self.mute_label.set_markup(self.get_muted())

    def get_muted(self):
        if self.sink.muted:
            return self.muted_icon
        else:
            return self.unmuted_icon


class Volume(WidgetBox):

    def __init__(self, **kwargs):
        self.icon = kwargs.get("icon", "")
        self.timer = kwargs.get("timer", 5)
        self.icon_size = kwargs.get("icon_size", 20)
        self.click_to_mute = kwargs.get("click_to_mute", False)
        self.muted_icon = kwargs.get("muted_icon", "󰝟")
        self.unmuted_icon = kwargs.get("unmuted_icon", "󰕾")
        self.volume = VolumeModule()
        self.default_button_dict = {}
        super().__init__(icon=self.icon, timer=self.timer, icon_size=self.icon_size)

    def run(self):
        super().run()

        # Connect signals for dropdown
        self.dropdown.connect("show", self.on_show)
        self.dropdown.connect("closed", self.on_close)

    def populate_dropdown(self):
        sinks = self.volume.get_sinks()
        for sink in sinks:
            sink_label = Gtk.Label()
            # Split string to insert new line at every 25 character
            # to line wrap long sink names
            sink_text = "\n".join(re.findall(".{1,25}", sink.name))
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
            slider.set_value(sink.volume)
            slider.set_name(f"{sink.id}")
            slider.connect("value-changed", self.on_slider_change)
            slider_box.append(slider)
            mute_button = MuteButton(
                icon_size=self.icon_size,
                sink=sink,
                muted_icon=self.muted_icon,
                unmuted_icon=self.unmuted_icon,
                volume_module=self.volume,
            )
            slider_box.append(mute_button)
            set_default_button = Gtk.Button(label="Set as default")
            self.default_button_dict[sink.id] = set_default_button
            set_default_button.connect(
                "clicked",
                lambda btn, sink_id=sink.id: self.on_default_click(btn, sink_id),
            )
            if sink.default:
                set_default_button.set_sensitive(False)
            slider_box.append(set_default_button)
            self.dropdown.add(slider_box)
        return True

    def set_text(self):
        self.text_label.set_label(f"{self.volume.get_volume("@DEFAULT_AUDIO_SINK@")}%")
        return True

    def on_slider_change(self, scale):
        scale_id = int(scale.get_name())
        sink = list(filter(lambda s: s.id == scale_id, self.volume.get_sinks()))[0]
        volume = scale.get_value() / 100
        self.volume.set_volume(scale_id, volume)
        if scale_id == sink.id:
            self.set_text()

    def on_scroll(self, controller, x, y):
        if y < 0:
            self.volume.set_volume("@DEFAULT_AUDIO_SINK@", "5%+")
            self.set_text()
        elif y > 0:
            self.volume.set_volume("@DEFAULT_AUDIO_SINK@", "5%-")
            self.set_text()

    def on_default_click(self, user_data, sink_id):
        current_default = self.volume.get_default_sink().id
        current_default_button = self.default_button_dict.get(current_default)
        if current_default_button:
            self.volume.set_default_sink(sink_id)
            current_default_button.set_sensitive(True)
            user_data.set_sensitive(False)

    def on_click(self, user_data):
        if self.click_to_mute:
            self.toggle_mute("@DEFAULT_AUDIO_SINK@")
        else:
            self.dropdown.popup()

    def on_middle_click(self, sequence, user_data):
        if not self.click_to_mute:
            self.volume.toggle_mute("@DEFAULT_AUDIO_SINK@")
        else:
            self.dropdown.popup()

    def on_right_click(self, sequence, user_data):
        self.volume.change_default_sink()

    def on_show(self, user_data):
        self.populate_dropdown()

    def on_close(self, user_data):
        self.dropdown.clear()
        self.default_button_dict.clear()
