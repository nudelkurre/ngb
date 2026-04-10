from collections import namedtuple
import socket
import re
import os
import json
from operator import itemgetter
import traceback
import random

from .namedtuples import NamedTuples
from .windowmanageripc import WindowManagerIPC

Workspace = NamedTuples.Workspace
Window = NamedTuples.Window


class NiriIPC(WindowManagerIPC):
    focused_output = ""
    focused_workspace_id = ""
    active_workspaces = {}

    def __init__(self):
        super().__init__()
        self.sock_req = f"{os.environ.get('NIRI_SOCKET')}"
        self.connect()

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
                    if len(part) < 1024:
                        break
                response = response.decode("utf-8")
                response = json.loads(response)
                if isinstance(response, dict):
                    response = response.get("Ok", {}).get(cmd, [])
                    socket_data = response
            except socket.error as e:
                print(e)
            except socket.timeout:
                print("Error: Socket timed out")
            except Exception:
                traceback.print_exc()
                print("-" * 15)
            finally:
                return socket_data

    def parse_workspace(self, ws):
        parsed_ws = list()
        self.get_outputs()
        for wss in ws:
            ws_dict = dict()
            if (
                wss != {}
                and wss["active_window_id"] != None
                and self.active_workspaces.get(wss.get("output", "")) != None
                or (wss["is_active"] and wss["active_window_id"] == None)
            ):
                ws_dict["id"] = wss.get("idx", 0)
                ws_dict["name"] = wss.get("name", str(wss.get("id", 0)))
                ws_dict["monitor"] = wss.get("output", "")
                ws_dict["active"] = wss.get("is_active", False)
                ws_dict["urgent"] = wss.get("is_urgent", False)
                ws_dict["focused"] = wss.get("is_focused", False)
                self.active_workspaces.get(wss.get("output", "")).append(
                    [wss.get("name", "0"), wss.get("idx", 0)]
                )
                if wss["is_focused"]:
                    self.focused_output = wss.get("output", "")
                    self.focused_workspace_id = wss.get("idx", 0)
            if ws_dict != {}:
                parsed_ws.append(ws_dict)
        for out in self.active_workspaces.keys():
            self.active_workspaces[out] = sorted(
                self.active_workspaces[out], key=itemgetter(1)
            )
        return parsed_ws

    def get_workspaces(self):
        workspaces = self.send_to_socket("Workspaces")
        if workspaces:
            parsed_ws = self.parse_workspace(workspaces)
            ws_list = list()
            for p in parsed_ws:
                ws_list.append(
                    Workspace(
                        id=p.get("id", 0),
                        name=p.get("name", "0"),
                        focused=p.get("focused", False),
                        output=p.get("monitor", ""),
                        urgent=p.get("urgent", False),
                    )
                )
            return ws_list
        return []

    def get_outputs(self):
        outputs = self.send_to_socket("Outputs")
        if outputs:
            parsed_outputs = list(outputs.keys())
            for out in parsed_outputs:
                self.active_workspaces[out] = []

    def get_windows(self):
        windows = self.send_to_socket("Windows")
        windows_list = []
        if windows:
            for w in windows:
                windows_list.append(
                    Window(
                        id=w.get("id"),
                        title=w.get("title"),
                        focused=w.get("is_focused"),
                    )
                )
        return windows_list

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
        if workspace == "next_on_output":
            for index, idx in enumerate(self.active_workspaces[self.focused_output]):
                if self.focused_workspace_id == idx[1]:
                    next_ws = self.active_workspaces[self.focused_output][
                        (index + 1) % len(self.active_workspaces[self.focused_output])
                    ]
                    return {
                        "Action": {
                            "FocusWorkspace": {"reference": {"Name": next_ws[0]}}
                        }
                    }
        elif workspace == "prev_on_output":
            for index, idx in enumerate(self.active_workspaces[self.focused_output]):
                if self.focused_workspace_id == idx[1]:
                    prev_ws = self.active_workspaces[self.focused_output][
                        (index - 1) % len(self.active_workspaces[self.focused_output])
                    ]
                    return {
                        "Action": {
                            "FocusWorkspace": {"reference": {"Name": prev_ws[0]}}
                        }
                    }
        else:
            return {"Action": {"FocusWorkspace": {"reference": {"Name": workspace}}}}

    def close_window(self, id):
        self.command(f"close {id}")

    def focus_window(self, id):
        self.command(f"window {id}")
