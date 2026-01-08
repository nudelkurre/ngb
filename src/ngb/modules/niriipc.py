from collections import namedtuple
import socket
import re
import os
import json
from operator import itemgetter

from .windowmanageripc import WindowManagerIPC


class NiriIPC(WindowManagerIPC):
    focused_output = ""
    focused_workspace_id = ""
    active_workspaces = {}

    def __init__(self):
        self.sock_req = f"{os.environ.get('NIRI_SOCKET')}"

    def send_to_socket(self, cmd):
        usocket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            usocket.connect(self.sock_req)
            try:
                usocket.sendall(self.translate_cmd(cmd))
                usocket.sendall("\n".encode("utf-8"))
                response = ""
                while True:
                    part = usocket.recv(1024)
                    response += part.decode("utf-8")
                    if len(part) < 1024:
                        break
                return json.loads(response)
            except socket.error as e:
                print(e)
            except socket.timeout:
                print("Error: Socket timed out")
            except Exception as e:
                print(f"Error: {e}")
        except ConnectionRefusedError:
            print("Connection to the UNIX socket refused.")
        except socket.error as e:
            print(f"Error open socket: {e}")
        finally:
            usocket.close()

    def parse_workspace(self, ws):
        parsed_ws = list()
        self.get_outputs()
        for wss in ws:
            ws_dict = dict()
            if (
                wss != {}
                and wss["active_window_id"] != None
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
        workspace = namedtuple(
            "workspace", ["id", "name", "focused", "output", "urgent"]
        )
        workspaces = self.send_to_socket("Workspaces")
        if workspaces and "Ok" in workspaces:
            parsed_ws = self.parse_workspace(
                workspaces.get("Ok", {}).get("Workspaces", [])
            )
            ws_list = list()
            for p in parsed_ws:
                ws_list.append(
                    workspace(
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
        if outputs and "Ok" in outputs:
            parsed_outputs = list(outputs.get("Ok", {}).get("Outputs", {}).keys())
            for out in parsed_outputs:
                self.active_workspaces[out] = []

    def translate_cmd(self, cmd):
        cmd_list = cmd.split()
        new_cmd = ""
        if cmd_list[0] == "workspace":
            new_cmd = self.goto_workspace(cmd_list[1])
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

    def command(self, cmd):
        self.send_to_socket(cmd)
