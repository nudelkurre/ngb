import socket
import re
import os
import struct
import json
import traceback

from gi.repository import Gio, GLib

from ngb.types import NamedTuples
from ngb.utils import log_error, log_warning
from .windowmanageripc import WindowManagerIPC

Workspace = NamedTuples.Workspace
Window = NamedTuples.Window
Monitor = NamedTuples.Monitor


class SwayIPC(WindowManagerIPC):

    event_types = {
        "0x1": "get_workspaces",
        "0x4": "get_tree",
        "0x80000000": "workspace",
        "0x80000001": "output",
        "0x80000002": "mode",
        "0x80000003": "window",
        "0x80000004": "barconfig_update",
        "0x80000005": "binding",
        "0x80000006": "shutdown",
        "0x80000007": "tick",
        "0x80000014": "bar_state_update",
        "0x80000015": "input",
    }

    def __init__(self, **kwargs):
        self.timer = kwargs.get("timer", 1)
        super().__init__(timer=self.timer)
        self.socket_path = f"{os.environ.get('SWAYSOCK')}"

        self.commands = [
            self.encode_cmd("GET_WORKSPACES", 1),
            self.encode_cmd("GET_TREE", 4),
            self.encode_cmd("['workspace', 'window']", 2),
        ]

    def encode_cmd(self, msg, msg_type=0):
        header = b"i3-ipc" + struct.pack("@II", len(msg), msg_type)
        return header + msg.encode("utf-8")

    def _parse_message(self, message_type, payload):
        data = json.loads(payload)
        event_type = self.event_types.get(hex(message_type))
        match event_type:
            case None:
                pass
            case "get_workspaces":
                workspaces = list()
                for workspace in data:
                    workspaces.append(
                        Workspace(
                            id=workspace.get("num", 0),
                            name=workspace.get("name", ""),
                            focused=workspace.get("focused", False),
                            output=workspace.get("output", ""),
                            urgent=workspace.get("urgent", False),
                            active=True,
                        )
                    )
                self.workspaces = sorted(workspaces, key=lambda ws: ws.id)
                self.emit("workspaces", self.workspaces)
            case "get_tree":
                windows = list()
                monitors = list()
                outputs = data.get("nodes", [])
                for output in outputs:
                    if output.get("name") == "__i3":
                        continue
                    workspaces = list()
                    out_nodes = output.get("nodes")
                    for on in out_nodes:
                        workspaces.append(on.get("num"))
                        ws_nodes = on.get("nodes")
                        for wsn in ws_nodes:
                            new_window = Window(
                                id=wsn.get("id", 0),
                                title=wsn.get("name", ""),
                                focused=wsn.get("focused", False),
                            )
                            windows.append(new_window)
                            if new_window.focused:
                                self.focused_window = new_window
                    workspaces = list(filter(None, workspaces))
                    monitors.append(
                        Monitor(
                            name=output.get("name", ""),
                            active=output.get("active", False),
                            workspaces=workspaces,
                            active_workspace=output.get("current_workspace"),
                        )
                    )
                self.windows = sorted(windows, key=lambda w: w.id)
                self.monitors = monitors
                self.emit("windows", self.windows)
                self.emit("monitors", self.monitors)
                self.emit("focused-window", self.focused_window)
            case "workspace":
                change = data.get("change")
                match change:
                    case "focus":
                        old = data.get("old", {})
                        current = data.get("current", {})
                        for index, workspace in enumerate(self.workspaces):
                            if workspace.id == old.get("num"):
                                self.workspaces[index].focused = False
                            elif workspace.id == current.get("num"):
                                self.workspaces[index].focused = True
                                if len(current.get("focus", [])) == 0:
                                    self.focused_window = Window()
                                    self.emit("focused-window", self.focused_window)
                    case "init":
                        current = data.get("current", {})
                        self.workspaces.append(
                            Workspace(
                                id=current.get("num", 0),
                                name=current.get("name", ""),
                                focused=current.get("focused", False),
                                output=current.get("output", ""),
                                urgent=current.get("urgent", False),
                                active=True,
                            )
                        )
                        self.workspaces = sorted(self.workspaces, key=lambda ws: ws.id)
                    case "empty":
                        old = data.get("old", {})
                        current = data.get("current", {})
                        index_to_remove = -1
                        for index, workspace in enumerate(self.workspaces):
                            if workspace.id == current.get("num"):
                                index_to_remove = index
                                break
                        if index_to_remove > -1:
                            self.workspaces.pop(index_to_remove)
                    case "rename":
                        current = data.get("current", {})
                        for index, workspace in enumerate(self.workspaces):
                            if workspace.id == current.get("num"):
                                self.workspaces[index].name = current.get("name", "")
                    case "urgent":
                        current = data.get("current", {})
                        for index, workspace in enumerate(self.workspaces):
                            if workspace.id == current.get("num"):
                                self.workspaces[index].urgent = current.get(
                                    "urgent", False
                                )
                self.emit("workspaces", self.workspaces)
            case "window":
                change = data.get("change")
                container = data.get("container", {})
                match change:
                    case "new":
                        new_window = Window(
                            id=container.get("id", 0),
                            title=container.get("name", ""),
                            focused=container.get("focused", False),
                        )
                        self.windows.append(new_window)
                    case "close":
                        index_to_remove = -1
                        for index, window in enumerate(self.windows):
                            if window.id == container.get("id"):
                                index_to_remove = index
                                break
                        if index_to_remove > -1:
                            self.windows.pop(index_to_remove)
                        self.focused_window = Window()
                    case "focus":
                        for index, window in enumerate(self.windows):
                            if window.id == container.get("id"):
                                self.windows[index].focused = container.get("focused")
                                self.focused_window = self.windows[index]
                    case "title":
                        for index, window in enumerate(self.windows):
                            if window.id == container.get("id"):
                                self.windows[index].title = container.get("name")
                self.emit("focused-window", self.focused_window)
                self.emit("windows", self.windows)
        return data

    def _read_next_line(self, listener):
        listener["_read_buffer"] = bytearray()
        listener["_read_target"] = 14
        listener["_read_phase"] = "header"
        self._read_more(listener)

    def _read_more(self, listener):
        remaining = listener["_read_target"] - len(listener["_read_buffer"])

        listener["input"].read_bytes_async(
            remaining,
            GLib.PRIORITY_DEFAULT,
            self._cancellable,
            self._on_line_read,
            listener,
        )

    def _on_line_read(self, stream, result, listener):
        try:
            chunk = stream.read_bytes_finish(result).get_data()
        except GLib.Error as error:
            self.emit("disconnected", str(error))
            return

        if not chunk:
            self.emit("disconnected", "Socket closed by peer")
            return

        listener["_read_buffer"].extend(chunk)

        if len(listener["_read_buffer"]) < listener["_read_target"]:
            self._read_more(listener)
            return

        if listener["_read_phase"] == "header":
            header = bytes(listener["_read_buffer"])

            if header[:6] != b"i3-ipc":
                self.emit("disconnected", "Invalid Sway IPC magic")
                return

            payload_length, message_type = struct.unpack("@II", header[6:14])

            listener["_message_type"] = message_type
            listener["_payload_length"] = payload_length
            listener["_read_buffer"] = bytearray()
            listener["_read_target"] = payload_length
            listener["_read_phase"] = "payload"

            if payload_length:
                self._read_more(listener)
                return

        payload = bytes(listener["_read_buffer"])

        try:
            event = self._parse_message(
                listener["_message_type"],
                payload.decode("utf-8"),
            )
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            print(f"Could not parse Sway IPC payload: {error}")

        self._read_next_line(listener)

    def send_to_socket(self, cmd):
        socket_data = []
        try:
            self.sock_connect()
            self.usocket.sendall(self.encode_cmd(cmd, 0))
            response = bytes()
            while True:
                part = self.usocket.recv(1024)
                response += part
                if len(part) < 1024:
                    break
            response = response[14:].decode("utf-8")
            match = re.search(r"^[\[\{][\W\w]*[\]\}]$", response)
            if match:
                parsed_response = json.loads(match.group(0))
            else:
                parsed_response = []
            self.disconnect()
            socket_data = parsed_response
        except socket.error as e:
            log_error(e)
        except Exception as e:
            log_error(e)
        finally:
            return socket_data

    def close_window(self, id):
        self.command(f"[con_id={id}] kill")

    def focus_window(self, id):
        self.command(f"[con_id={id}] focus")
