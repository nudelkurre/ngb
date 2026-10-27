import socket
import os
import json
from gi.repository import Gio, GLib, GObject

from ngb.utils import log_error, log_warning


class WindowManagerIPC(GObject.Object):
    __gsignals__ = {
        "focused-window": (
            GObject.SignalFlags.RUN_LAST,
            None,
            (object,),
        ),
        "monitors": (
            GObject.SignalFlags.RUN_LAST,
            None,
            (object,),
        ),
        "windows": (
            GObject.SignalFlags.RUN_LAST,
            None,
            (object,),
        ),
        "workspaces": (
            GObject.SignalFlags.RUN_LAST,
            None,
            (object,),
        ),
        "disconnected": (
            GObject.SignalFlags.RUN_LAST,
            None,
            (str,),
        ),
    }

    def __init__(self, **kwargs):
        super().__init__()
        self.usocket = None
        self.timer = kwargs.get("timer", 1)

        self.workspaces = list()
        self.monitors = list()
        self.windows = list()
        self.focused_window = None

        self.socket_path = None
        self._cancellable = Gio.Cancellable()
        self._listener = list()

    def start(self):
        if self.socket_path is None:
            return

        for command in self.commands:
            listener = {
                "client": Gio.SocketClient.new(),
                "connection": None,
                "input": None,
                "output": None,
                "command": command,
            }
            self._listener.append(listener)

            address = Gio.UnixSocketAddress.new(self.socket_path)
            listener["client"].connect_async(
                address,
                self._cancellable,
                self._on_connected,
                listener,
            )

    def _on_connected(self, client, result, listener):
        try:
            listener["connection"] = listener["client"].connect_finish(result)
            listener["input"] = Gio.DataInputStream.new(
                listener["connection"].get_input_stream()
            )
            listener["output"] = listener["connection"].get_output_stream()

            listener["output"].write_all_async(
                listener["command"],
                GLib.PRIORITY_DEFAULT,
                self._cancellable,
                self._on_subscribe_sent,
                listener,
            )
        except GLib.Error as error:
            self.emit("disconnected", str(error))

    def _on_subscribe_sent(self, output, result, _user_data):
        try:
            output.write_all_finish(result)
            self._read_next_line(_user_data)
        except GLib.Error as error:
            self.emit("disconnected", str(error))

    def _read_next_line(self, listener):
        listener["input"].read_line_async(
            GLib.PRIORITY_DEFAULT,
            self._cancellable,
            self._on_line_read,
            listener,
        )

    def _parse_line(self, line, command):
        return ""

    def _on_line_read(self, stream, result, _user_data):
        try:
            line = stream.read_line_finish(result)
        except GLib.Error as error:
            self.emit("disconnected", str(error))
            return

        if line is None:
            self.emit("disconnected", "Socket closed by peer")
            return

        try:
            event = self._parse_line(line, _user_data["command"].decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            self._read_next_line(_user_data)
            return

        self._read_next_line(_user_data)

    def stop(self):
        self._cancellable.cancel()
        if self._connection is not None:
            self._connection.close(None)
            self._connection = None

    def sock_connect(self):
        self.usocket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.usocket.settimeout(self.timer * 3)
        try:
            self.usocket.connect(self.socket_path)
        except ConnectionRefusedError:
            log_error("Connection to the UNIX socket refused.")
        except socket.error as e:
            log_error(f"Error open socket: {e}")

    def disconnect(self):
        self.usocket.close()

    def is_connected(self):
        if self.usocket is None:
            log_warning("No socket created")
            print("No socket created")
            return False
        try:
            self.usocket.sendall(b"")
            return True
        except socket.error:
            log_error("IPC socket not connected")
            print("IPC socket not connected")
            return False

    def send_to_socket(self, cmd):
        return []

    def close_window(self, id):
        pass

    def focus_window(self, id):
        pass

    def translate_cmd(self, cmd):
        return ""

    def command(self, cmd):
        return self.send_to_socket(cmd)
