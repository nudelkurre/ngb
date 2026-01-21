from collections import namedtuple
import socket
import re
import os
import struct
import json

from .namedtuples import NamedTuples
from .windowmanageripc import WindowManagerIPC

Workspace = NamedTuples.Workspace


class SwayIPC(WindowManagerIPC):

    def __init__(self):
        self.sock_req = f"{os.environ.get('SWAYSOCK')}"

    def send_to_socket(self, cmd):
        usocket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            usocket.connect(self.sock_req)
            try:
                usocket.sendall(self.translate_cmd(cmd))
                usocket.sendall("\n".encode("utf-8"))
                response = bytes()
                while True:
                    part = usocket.recv(1024)
                    response += part
                    if len(part) < 1024:
                        break
                response = response[14:].decode("utf-8")
                match = re.search(r"^[\[\{][\W\w]*[\]\}]$", response).group(0)
                if match:
                    parsed_response = json.loads(match)
                else:
                    parsed_response = []
                return parsed_response
            except socket.error as e:
                print(e)
        except ConnectionRefusedError:
            print("Connection to the UNIX socket refused.")
        except socket.error as e:
            print(f"Error open socket: {e}")
        finally:
            usocket.close()

    def get_workspaces(self):
        wss = self.send_to_socket("GET_WORKSPACES")
        ws_list = list()
        for p in wss:
            ws_list.append(
                Workspace(
                    id=p.get("num", 0),
                    name=p.get("name", "0"),
                    focused=p.get("focused", False),
                    output=p.get("output", ""),
                    urgent=p.get("urgent", False),
                )
            )
        return ws_list

    def get_windows(self):
        windows = self.send_to_socket("GET_TREE")
        root_nodes = windows.get("nodes", [])
        output_nodes = []
        for rn in root_nodes:
            if rn.get("name") != "__i3":
                output_nodes += rn.get("nodes", [])
        window_nodes = []
        for on in output_nodes:
            window_nodes += on.get("nodes", [])
        window_list = []
        for wn in window_nodes:
            wn_dict = {}
            wn_dict["id"] = wn.get("id", 0)
            wn_dict["title"] = wn.get("name", "")
            wn_dict["focused"] = wn.get("focused", False)
            window_list.append(wn_dict)
        return window_list

    def close_window(self, id):
        self.command(f"[con_id={id}] kill")

    def focus_window(self, id):
        self.command(f"[con_id={id}] focus")

    def translate_cmd(self, cmd):
        match cmd:
            case "GET_WORKSPACES":
                cmd_id = 1
            case "SUBSCRIBE":
                cmd_id = 2
            case "GET_OUTPUTS":
                cmd_id = 3
            case "GET_TREE":
                cmd_id = 4
            case "GET_MARKS":
                cmd_id = 5
            case "GET_BAR_CONFIG":
                cmd_id = 6
            case "GET_VERSION":
                cmd_id = 7
            case "GET_BINDING_MODES":
                cmd_id = 8
            case "GET_CONFIG":
                cmd_id = 9
            case "SEND_TICK":
                cmd_id = 10
            case "SYNC":
                cmd_id = 11
            case "GET_BINDING_STATE":
                cmd_id = 12
            case "GET_INPUTS":
                cmd_id = 100
            case "GET_SEATS":
                cmd_id = 101
            case _:
                cmd_id = 0

        magic_string = "i3-ipc".encode("utf-8")
        cmd_len = struct.pack("@i", len(cmd))
        cmd_type = struct.pack("@i", cmd_id)

        cmd_str = magic_string + cmd_len + cmd_type + cmd.encode("utf8")
        return cmd_str
