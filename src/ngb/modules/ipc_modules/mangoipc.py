import subprocess
import re
import os
import json

from ngb.types import NamedTuples
from ngb.utils import log_error, log_warning
from .windowmanageripc import WindowManagerIPC

Workspace = NamedTuples.Workspace
Window = NamedTuples.Window


class MangoIPC(WindowManagerIPC):

    def __init__(self, **kwargs):
        self.timer = kwargs.get("timer", 1)
        super().__init__(timer=self.timer)

    def send_to_socket(self, cmd):
        socket_data = subprocess.run(
            self.translate_cmd(cmd), capture_output=True, text=True, timeout=self.timer
        ).stdout
        socket_data = json.loads(socket_data)
        return socket_data

    def get_workspaces(self):
        workspace_list = []
        wss = self.send_to_socket("get all-tags").get("all_tags", [])
        focused_client = self.send_to_socket("get focusing-client")
        focused_monitor = focused_client.get("monitor")
        for ws in wss:
            monitor = ws.get("monitor", "")
            tags = ws.get("tags", [])
            for tag in tags:
                if tag.get("client_count") > 0:
                    is_focused = focused_monitor == monitor and tag.get(
                        "is_active", False
                    )
                    workspace_list.append(
                        Workspace(
                            id=tag.get("index", 0),
                            name=str(tag.get("index", 0)),
                            focused=is_focused,
                            output=monitor,
                            urgent=tag.get("is_urgent", False),
                        )
                    )
                elif tag.get("is_active"):
                    workspace_list.append(
                        Workspace(
                            id=tag.get("index", 0),
                            name=str(tag.get("index", 0)),
                            focused=True,
                            output=monitor,
                            urgent=tag.get("is_urgent", False),
                        )
                    )
        return workspace_list

    def get_focused_window(self):
        return self.send_to_socket("get focusing-client").get("title", "")

    def get_windows(self):
        window_list = []
        windows = self.send_to_socket("get all-clients").get("clients", [])
        for window in windows:
            window_list.append(
                Window(
                    id=window.get("id", 0),
                    title=window.get("title", ""),
                    focused=window.get("is_focused", False),
                )
            )
        return window_list

    def close_window(self, id):
        self.command(f"dispatch killclient client,{id}")

    def focus_window(self, id):
        self.command(f"dispatch focusid client,{id}")

    def get_current_tags(self):
        tags = self.send_to_socket("get all-monitors").get("monitors", [])
        monitor = [x if x.get("active") else None for x in tags]
        monitor = list(filter(None, monitor))[0]
        monitor_tags = [
            (
                x.get("index", 0)
                if x.get("client_count") > 0 or x.get("is_active")
                else None
            )
            for x in monitor.get("tags", [])
        ]
        monitor_tags = list(filter(None, monitor_tags))
        active_tags = monitor.get("active_tags")
        return {"tags": monitor_tags, "active": active_tags[0]}

    def translate_cmd(self, cmd):
        cmd_list = cmd.split()
        new_cmd = ""
        if cmd_list[0] == "workspace":
            new_cmd = self.goto_workspace(cmd_list[1])
        else:
            new_cmd = cmd
        new_cmd = f"mmsg {new_cmd}".split()
        return new_cmd

    def goto_workspace(self, workspace):
        if workspace == "next_on_output":
            tags_dict = self.get_current_tags()
            tags = tags_dict.get("tags", [])
            current_tag = tags_dict.get("active", 0)
            for index, value in enumerate(tags):
                if value == current_tag:
                    return f"dispatch view,{tags[(index + 1) % (len(tags))]}"
        elif workspace == "prev_on_output":
            tags_dict = self.get_current_tags()
            tags = tags_dict.get("tags", [])
            current_tag = tags_dict.get("active", 0)
            for index, value in enumerate(tags):
                if value == current_tag:
                    return f"dispatch view,{tags[(index - 1) % (len(tags))]}"
        else:
            tags_dict = self.get_current_tags()
            return f"dispatch view,{workspace}"
