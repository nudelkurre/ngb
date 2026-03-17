import socket


class WindowManagerIPC:
    def __init__(self):
        self.usocket = None

    def connect(self):
        self.usocket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            self.usocket.connect(self.sock_req)
        except ConnectionRefusedError:
            print("Connection to the UNIX socket refused.")
        except socket.error as e:
            print(f"Error open socket: {e}")

    def disconnect(self):
        self.usocket.close()

    def is_connected(self):
        if self.usocket is None:
            print("No socket created")
            return False
        try:
            self.usocket.sendall(b"")
            return True
        except socket.error:
            print("IPC socket not connected")
            return False

    def send_to_socket(self, cmd):
        return {}

    def parse_workspace(self, ws):
        return []

    def get_workspaces(self):
        return []

    def get_windows(self):
        return []

    def get_focused_window(self):
        windows = self.get_windows()
        for window in windows:
            if window.focused:
                return window.title
        return ""

    def close_window(self, id):
        pass

    def focus_window(self, id):
        pass

    def translate_cmd(self, cmd):
        return ""

    def command(self, cmd):
        return self.send_to_socket(cmd)
