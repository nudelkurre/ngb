from shutil import which

import subprocess
import re

from .namedtuples import NamedTuples

VolumeSink = NamedTuples.VolumeSink


class VolumeModule:
    path = which("wpctl")

    def __init__(self):
        pass

    def change_default_sink(self):
        default = self.get_default_sink()
        sinks = self.get_sinks()
        next_sink = 0
        for index, sink in enumerate(sinks):
            if sink == default:
                next_sink = (index + 1) % len(sinks)
        self.set_default_sink(sinks[next_sink].id)

    def get_default_sink(self):
        sinks = self.get_sinks()
        for sink in sinks:
            if sink.default:
                return sink

    def get_sinks(self):
        if self.path:
            sink_list = []
            proc_out = subprocess.run(
                "wpctl status".split(), capture_output=True, text=True
            ).stdout
            audio = re.search(r"(Audio[\W\w]+Video)", proc_out).group(1)
            sinks = re.search(r"(Sinks:[\W\w]+Sources:)", audio).group(1)
            for s in sinks.split("\n"):
                sink = re.search(
                    r"\s*(?P<default>\*?)\s*(?P<id>\d+)\.\s*(?P<name>[\w\s\d\[\]\(\)-\/]+)\s*\[vol:\s*(?P<volume>\d+\.\d+)\s?(?P<muted>MUTED)*\]",
                    s,
                )
                if sink:
                    sink_list.append(
                        VolumeSink(
                            id=int(sink.group("id")),
                            name=sink.group("name").lstrip().rstrip(),
                            volume=int(float(sink.group("volume")) * 100),
                            muted=True if sink.group("muted") else False,
                            default=True if sink.group("default") == "*" else False,
                        )
                    )
            return sink_list

    def get_sources(self):
        if self.path:
            source_list = []
            proc_out = subprocess.run(
                "wpctl status".split(), capture_output=True, text=True
            ).stdout
            audio = re.search(r"(Audio[\W\w]+Video)", proc_out).group(1)
            sources = re.search(r"(Sources:[\W\w]+Filters:)", audio).group(1)
            for s in sources.split("\n"):
                source = re.search(
                    r"\s*(?P<default>\*?)\s*(?P<id>\d+)\.\s*(?P<name>[\w\s\d\[\]\(\)-\/]+)\s*\[vol:\s*(?P<volume>\d+\.\d+)\s?(?P<muted>MUTED)*\]",
                    s,
                )
                if source:
                    source_list.append(
                        VolumeSink(
                            id=int(source.group("id")),
                            name=source.group("name").lstrip().rstrip(),
                            volume=int(float(source.group("volume")) * 100),
                            muted=True if source.group("muted") else False,
                            default=True if source.group("default") == "*" else False,
                        )
                    )
            return source_list

    def get_volume(self, id):
        if self.path:
            volume = subprocess.run(
                f"wpctl get-volume {id}".split(), capture_output=True, text=True
            ).stdout
            volume_level = int(float(re.search(r"(\d?\.\d{2})", volume).group(1)) * 100)
            return volume_level
        return "wpctl not installed"

    def set_default_sink(self, id):
        if self.path:
            subprocess.run(f"wpctl set-default {id}".split())

    def set_volume(self, id, volume):
        if self.path:
            subprocess.run(f"wpctl set-volume {id} {volume}".split())

    def toggle_mute(self, id):
        if self.path:
            subprocess.run(f"wpctl set-mute {id} toggle".split())
