import socket
import re
import os
import json

from operator import itemgetter
import traceback
import random
from dataclasses import dataclass, field

from gi.repository import Gio, GLib

from ngb.types import NamedTuples
from ngb.utils import log_error, log_warning
from .windowmanageripc import WindowManagerIPC

# Workspace = NamedTuples.Workspace
Window = NamedTuples.Window
Monitor = NamedTuples.Monitor


@dataclass
class Workspace(NamedTuples.Workspace):
    global_id: int = 0
    windows: set[int] = field(default_factory=set)


@dataclass
class Window(NamedTuples.Window):
    workspace: int = 0


class NiriIPC(WindowManagerIPC):
    focused_output = Monitor()

    def __init__(self, **kwargs):
        self.timer = kwargs.get("timer")
        super().__init__(timer=self.timer)
        self.socket_path = f"{os.environ.get('NIRI_SOCKET')}"
        self.sock_connect()
        self.commands = [(json.dumps("EventStream") + "\n").encode("utf-8")]

    def _parse_line(self, line, command):
        data = json.loads(line[0].decode("utf-8"))
        keys = [*data][0]
        match keys:
            case "WindowsChanged":
                windows = data.get("WindowsChanged", {}).get("windows", [])
                self.windows = list()
                for window in windows:
                    window_id = window.get("id", 0)
                    workspace_id = window.get("workspace_id", 0)
                    changed_window = Window(
                        id=window_id,
                        title=window.get("title", ""),
                        focused=window.get("is_focused", False),
                        workspace=workspace_id,
                    )
                    self.windows.append(changed_window)
                    if changed_window.focused:
                        self.focused_window = changed_window
                        self.emit("focused-window", self.focused_window)
                    for index, workspace in enumerate(self.workspaces):
                        if workspace.global_id == workspace_id:
                            self.workspaces[index].windows.add(window_id)
                            break
                self.windows = sorted(self.windows, key=lambda window: window.id)
                self.emit("windows", self.windows)
            case "WindowFocusChanged":
                focused_window_id = data.get("WindowFocusChanged", {}).get("id", 0)
                if focused_window_id is None:
                    self.focused_window = Window()
                    self.emit("focused-window", self.focused_window)
                else:
                    for index, window in enumerate(self.windows):
                        if window.id == focused_window_id:
                            self.windows[index].focused = True
                            self.focused_window = window
                        else:
                            if window.focused:
                                self.windows[index].focused = False
                    self.windows = sorted(self.windows, key=lambda window: window.id)
                    self.emit("windows", self.windows)
                    self.emit("focused-window", self.focused_window)
            case "WindowClosed":
                closed_window = data.get("WindowClosed", {})
                window_id = closed_window.get("id", 0)
                window_list = self.windows
                index_to_remove = -1
                for index, window in enumerate(window_list):
                    if window.id == window_id:
                        index_to_remove = index
                        break
                if index_to_remove > -1:
                    window_list.pop(index_to_remove)
                for index, workspace in enumerate(self.workspaces):
                    if window_id in workspace.windows:
                        self.workspaces[index].windows.remove(window_id)
                        if (
                            self.workspaces[index].windows == set()
                            and self.workspaces[index].focused == False
                        ):
                            self.workspaces[index].active = False
                self.windows = window_list
                self.emit("windows", self.windows)
                self.emit("workspaces", self.workspaces)
            case "WindowOpenedOrChanged":
                changed_window = data.get("WindowOpenedOrChanged", {}).get("window", {})
                changed_window_id = changed_window.get("id")
                workspace_id = changed_window.get("workspace_id")
                new_window = Window(
                    id=changed_window_id,
                    title=changed_window.get("title", ""),
                    focused=changed_window.get("is_focused", False),
                    workspace=changed_window.get("workspace_id", 0),
                )
                id_index = -1
                for index, window in enumerate(self.windows):
                    if changed_window_id == window.id:
                        id_index = index
                        break
                if id_index > -1:
                    self.windows[id_index] = new_window
                elif id_index == -1:
                    self.windows.append(new_window)
                if new_window.focused:
                    self.focused_window = new_window
                    self.emit("focused-window", self.focused_window)
                for index, workspace in enumerate(self.workspaces):
                    if workspace.global_id == workspace_id:
                        self.workspaces[index].windows.add(changed_window_id)
                self.emit("windows", self.windows)
            case "WorkspaceActivated":
                activated_workspace = data.get("WorkspaceActivated", {})
                activated_id = activated_workspace.get("id", 0)
                activated_focus = activated_workspace.get("focused", False)
                activated_monitor = ""

                workspaces = self.workspaces
                for workspace in workspaces:
                    if workspace.global_id == activated_id:
                        activated_monitor = workspace.output
                for index, workspace in enumerate(workspaces):
                    if workspace.global_id == activated_id:
                        workspaces[index].active = True
                        workspaces[index].focused = activated_focus
                        for m_index, monitor in enumerate(self.monitors):
                            if monitor.name == activated_monitor:
                                if activated_id not in monitor.workspaces:
                                    self.monitors[m_index].workspaces.append(
                                        activated_id
                                    )
                                    self.monitors[m_index].workspaces = sorted(
                                        self.monitors[m_index].workspaces
                                    )
                                if workspace.global_id in monitor.workspaces:
                                    self.monitors[m_index].active_workspace = (
                                        activated_id
                                    )
                    else:
                        if (
                            workspace.output == activated_monitor
                            and len(workspace.windows) < 1
                        ):
                            workspaces[index].active = False
                            for m_index, monitor in enumerate(self.monitors):
                                if (
                                    monitor.name == activated_monitor
                                    and workspace.global_id in monitor.workspaces
                                ):
                                    self.monitors[m_index].workspaces.remove(
                                        workspace.global_id
                                    )
                                    # print(self.monitors[m_index])
                                    break
                        workspaces[index].focused = False
                for monitor in self.monitors:
                    if monitor.name == activated_monitor:
                        self.focused_output = monitor
                workspaces = sorted(
                    workspaces, key=lambda workspace: workspace.global_id
                )
                self.workspaces = workspaces
                self.emit("workspaces", self.workspaces)
                self.emit("monitors", self.monitors)
            case "WorkspacesChanged":
                workspaces = data.get("WorkspacesChanged", {}).get("workspaces", [])
                self.workspaces = list()
                monitors = dict()
                for workspace in workspaces:
                    output = workspace.get("output")
                    global_id = workspace.get("id", 0)
                    is_focused = workspace.get("is_focused")
                    is_active = (
                        workspace.get("is_active")
                        or workspace.get("active_window_id") is not None
                    )
                    if output not in monitors.keys():
                        monitors[output] = dict()
                    if "workspaces" not in monitors.get(output, {}).keys():
                        monitors[output]["workspaces"] = list()
                    if is_active:
                        monitors[output]["workspaces"].append(global_id)
                    if is_focused:
                        monitors[output]["active_workspace"] = global_id
                    self.workspaces.append(
                        Workspace(
                            id=workspace.get("idx", 0),
                            global_id=global_id,
                            name=workspace.get("name", "0"),
                            focused=workspace.get("is_focused", False),
                            output=workspace.get("output", ""),
                            urgent=workspace.get("is_urgent", False),
                            active=is_active,
                        )
                    )
                for monitor in monitors.keys():
                    self.monitors.append(
                        Monitor(
                            name=monitor,
                            workspaces=sorted(monitors[monitor].get("workspaces", [])),
                            active_workspace=monitors[monitor].get("active_workspace"),
                        )
                    )
                self.emit("monitors", self.monitors)
                self.workspaces = sorted(
                    self.workspaces, key=lambda workspace: workspace.global_id
                )
                self.emit("workspaces", self.workspaces)
            case "WorkspaceActiveWindowChanged":
                workspace_id = data.get("WorkspaceActiveWindowChanged", {}).get(
                    "workspace_id"
                )
                for index, workspace in enumerate(self.workspaces):
                    if workspace.global_id == workspace_id:
                        self.workspaces[index].active = True
                self.emit("workspaces", self.workspaces)
            case "WorkspaceUrgencyChanged":
                urgent_workspace = data.get("WorkspaceUrgencyChanged", {})
                for index, workspace in enumerate(self.workspaces):
                    if workspace.global_id == urgent_workspace.get("id", 0):
                        self.workspaces[index].urgent = urgent_workspace.get(
                            "urgent", False
                        )
                self.workspaces = sorted(
                    self.workspaces, key=lambda workspace: workspace.global_id
                )
                self.emit("workspaces", self.workspaces)

    def send_to_socket(self, cmd):
        socket_data = []
        if self.is_connected():
            try:
                self.usocket.sendall(self.translate_cmd(cmd))
                self.usocket.sendall("\n".encode("utf-8"))
                response = bytearray()
                while True:
                    part = self.usocket.recv(1024)
                    response.extend(part)
                    if response.find(b"\n") != -1:
                        break
                response = response.decode("utf-8")
                response = json.loads(response)
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

    def translate_cmd(self, cmd):
        cmd_list = cmd.split()
        new_cmd = ""
        if cmd_list[0] == "workspace":
            new_cmd = self.goto_workspace(cmd_list[1])
        elif cmd_list[0] == "window":
            new_cmd = {"Action": {"FocusWindow": {"id": int(cmd_list[1])}}}
        elif cmd_list[0] == "close":
            new_cmd = {"Action": {"CloseWindow": {"id": int(cmd_list[1])}}}
        else:
            new_cmd = cmd
        cmd_json = json.dumps(new_cmd).encode("utf-8")
        return cmd_json

    def goto_workspace(self, workspace):
        if not self.focused_output:
            return
        if workspace == "next_on_output":
            for index, ws in enumerate(self.focused_output.workspaces):
                if ws == self.focused_output.active_workspace:
                    next_ws = str(
                        self.focused_output.workspaces[
                            (index + 1) % len(self.focused_output.workspaces)
                        ]
                    )
                    return {
                        "Action": {"FocusWorkspace": {"reference": {"Name": next_ws}}}
                    }
        elif workspace == "prev_on_output":
            for index, ws in enumerate(self.focused_output.workspaces):
                if ws == self.focused_output.active_workspace:
                    prev_ws = str(
                        self.focused_output.workspaces[
                            (index - 1) % len(self.focused_output.workspaces)
                        ]
                    )
                    return {
                        "Action": {"FocusWorkspace": {"reference": {"Name": prev_ws}}}
                    }
        else:
            return {"Action": {"FocusWorkspace": {"reference": {"Name": workspace}}}}

    def close_window(self, id):
        self.command(f"close {id}")

    def focus_window(self, id):
        self.command(f"window {id}")
