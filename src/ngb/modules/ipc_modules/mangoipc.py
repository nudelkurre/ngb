import subprocess
import socket
import os
import json
from dataclasses import dataclass

from gi.repository import Gio, GLib

from ngb.types import NamedTuples
from ngb.utils import log_error, log_warning
from .windowmanageripc import WindowManagerIPC

Workspace = NamedTuples.Workspace
Monitor = NamedTuples.Monitor


@dataclass
class Window(NamedTuples.Window):
    output: str = ""


class MangoIPC(WindowManagerIPC):

    def __init__(self, **kwargs):
        self.timer = kwargs.get("timer", 1)
        super().__init__(timer=self.timer)
        self.socket_path = os.environ.get("MANGO_INSTANCE_SIGNATURE")
        self.commands = [
            self._encode_cmd("all-clients"),
            self._encode_cmd("all-monitors"),
            self._encode_cmd("all-tags"),
            self._encode_cmd("focusing-client"),
            self._encode_cmd("keymode"),
        ]

    def _encode_cmd(self, cmd):
        return f"watch {cmd}\n".encode("utf-8")

    def _parse_line(self, line, command):
        data = json.loads(line[0].decode("utf-8"))
        cmd = command.split()[1]
        match cmd:
            case "all-clients":
                windows = data.get("clients", [])
                self.windows = list()
                for window in windows:
                    self.windows.append(
                        Window(
                            id=str(window.get("id", 0)),
                            title=window.get("title", ""),
                            focused=window.get("is_focused", False),
                        )
                    )
                self.emit("windows", self.windows)
            case "all-monitors":
                monitors = data.get("monitors", [])
                self.monitors = list()
                for m in monitors:
                    name = m.get("name", "")
                    active = m.get("active", False)
                    tags = m.get("tags", [])
                    monitor_tags = [
                        (
                            tag.get("index")
                            if tag.get("client_count") > 0 or tag.get("is_active")
                            else None
                        )
                        for tag in tags
                    ]
                    monitor_tags = list(filter(None, monitor_tags))
                    active_tags = m.get("active_tags", [0])
                    self.monitors.append(
                        Monitor(
                            name=name,
                            active=active,
                            workspaces=monitor_tags,
                            active_workspace=active_tags[0],
                        )
                    )
                self.emit("monitors", self.monitors)
            case "all-tags":
                workspaces = data.get("all_tags", [])
                self.workspaces = list()
                if self.focused_window is None:
                    return
                for workspace in workspaces:
                    monitor = workspace.get("monitor", "")
                    tags = workspace.get("tags", [])
                    for tag in tags:
                        is_focused = self.focused_window.output == monitor and tag.get(
                            "is_active", False
                        )
                        if tag.get("client_count") > 0:
                            self.workspaces.append(
                                Workspace(
                                    id=tag.get("index", 0),
                                    name=str(tag.get("index", 0)),
                                    focused=is_focused,
                                    output=monitor,
                                    urgent=tag.get("is_urgent", False),
                                    active=True,
                                )
                            )
                        elif tag.get("is_active"):
                            self.workspaces.append(
                                Workspace(
                                    id=tag.get("index", 0),
                                    name=str(tag.get("index", 0)),
                                    focused=is_focused,
                                    output=monitor,
                                    urgent=tag.get("is_urgent", False),
                                    active=True,
                                )
                            )
                self.emit("workspaces", self.workspaces)
            case "focusing-client":
                self.focused_window = Window(
                    id=str(data.get("id", 0)),
                    title=data.get("title", ""),
                    focused=data.get("is_focused", False),
                    output=data.get("monitor", ""),
                )
                self.emit("focused-window", self.focused_window)
            case "keymode":
                self.keymode = data.get("keymode", "")
                self.emit("keymode", self.keymode)

    def send_to_socket(self, cmd):
        socket_data = []
        try:
            self.sock_connect()
            translated_cmd = self.translate_cmd(cmd)
            self.usocket.sendall(translated_cmd)
            self.usocket.sendall("\n".encode("utf-8"))
            response = bytearray()
            while True:
                part = self.usocket.recv(1024)
                response.extend(part)
                if response.find(b"\n") != -1:
                    break
            response = response.decode("utf-8")
            response = json.loads(response)
            self.disconnect()
            response = response.get("Ok", {})
            if isinstance(response, dict):
                response = response.get(cmd, [])
            socket_data = response
            return socket_data
        except socket.timeout:
            log_warning("Error: Socket timed out")
            return []
        except Exception as e:
            log_error(e)
            return []

    def close_window(self, id):
        self.command(f"dispatch killclient client,{id}")

    def focus_window(self, id):
        self.command(f"dispatch focusid client,{id}")

    def translate_cmd(self, cmd):
        cmd_list = cmd.split()
        new_cmd = ""
        if cmd_list[0] == "workspace":
            new_cmd = self.goto_workspace(cmd_list[1])
        else:
            new_cmd = cmd
        encoded = new_cmd.encode("utf-8")
        new_cmd = f"mmsg {new_cmd}".split()
        return encoded

    def goto_workspace(self, workspace):
        tags_dict = self.monitors
        active_monitor = list(
            filter(
                None,
                [(monitor if monitor.active else None) for monitor in tags_dict],
            )
        )[0]
        tags = active_monitor.workspaces
        current_tag = active_monitor.active_workspace
        if workspace == "next_on_output":
            for index, value in enumerate(tags):
                if value == current_tag:
                    return f"dispatch view,{tags[(index + 1) % (len(tags))]}"
        elif workspace == "prev_on_output":
            for index, value in enumerate(tags):
                if value == current_tag:
                    return f"dispatch view,{tags[(index - 1) % (len(tags))]}"
        else:
            return f"dispatch view,{workspace}"
