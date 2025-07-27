from collections import namedtuple
import socket
import re
import os
import i3ipc

from .windowmanageripc import WindowManagerIPC

class SwayIPC():
    conn = i3ipc.Connection()

    def get_workspaces(self):
        workspace = namedtuple("workspace", ["id", "name", "focused", "output", "urgent"])
        wss = self.conn.get_workspaces()
        ws_list = list()
        for p in wss:
            ws_list.append(workspace(id=p.num, name=p.name, focused=p.focused, output=p.output, urgent=p.urgent))
        return ws_list

    def command(self, cmd):
        self.conn.command(cmd)