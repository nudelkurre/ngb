from gi.repository import Gtk
from gi.repository import GLib
from shutil import which

import subprocess
import re

from ngb.modules import WidgetBox

class Headset(WidgetBox):
    def __init__(self):
        super().__init__(icon="󰋎")

    def set_text(self):
        shutil.which