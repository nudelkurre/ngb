from collections import namedtuple
import socket
import re
import os

class HyprlandIpc:
    def __init__(self):
        socket_location = f"{os.environ['XDG_RUNTIME_DIR']}/hypr/{os.environ['HYPRLAND_INSTANCE_SIGNATURE']}"
        self.sock_req = f"{socket_location}/.socket.sock"

    def send_to_socket(self, cmd):
        usocket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            usocket.connect(self.sock_req)
            try:
                usocket.sendall(self.translate_cmd(cmd))
                return usocket.recv(1024).decode()
            except socket.error as e:
                print(e)
        except ConnectionRefusedError:
            print("CONNCETION REFUSED!!!!!!!!!!!!!")
        except socket.error as e:
            print(f"Error open socket: {e}")
        finally:
            usocket.close()

    def parse_workspace(self, ws):
        ws_list = ws.split("\n\n")
        parsed_ws = list()
        for wss in ws_list:
            match = re.match(r"workspace ID (?P<id>\d+) \((?P<name>[\w]+)\) on monitor (?P<monitor>[\w-]+):", wss)
            ws_dict = dict()
            if(match):
                ws_dict["id"] = match.group("id")
                ws_dict["name"] = match.group("name")
                ws_dict["monitor"] = match.group("monitor")
            if(ws_dict != {}):
                parsed_ws.append(ws_dict)
        return parsed_ws

    def get_workspaces(self):
        workspace = namedtuple("workspace", ["name", "focused", "output", "urgent"])
        workspaces = self.send_to_socket("workspaces")
        active_workspace = self.send_to_socket("activeworkspace")
        active_id = self.parse_workspace(active_workspace)[0]["id"]
        parsed_ws = self.parse_workspace(workspaces)
        ws_list = list()
        for p in parsed_ws:
            ws_list.append(workspace(name=p["name"], focused=p["id"] == active_id, output=p["monitor"], urgent=False))
        return ws_list

    def translate_cmd(self, cmd):
        cmd_list = cmd.split()
        if(cmd_list[0] == "workspace"):
            match cmd_list[1]:
                case "next_on_output":
                    cmd_list[1] = "m+1"
                case "prev_on_output":
                    cmd_list[1] = "m-1"
            cmd_list.insert(0, "dispatch")
        return " ".join(cmd_list).encode()

    def command(self, cmd):
        self.send_to_socket(cmd)