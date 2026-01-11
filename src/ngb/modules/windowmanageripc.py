class WindowManagerIPC:
    def __init__(self):
        pass

    def send_to_socket(self, cmd):
        pass

    def parse_workspace(self, ws):
        return []

    def get_workspaces(self):
        return []

    def get_windows(self):
        return []

    def get_focused_window(self):
        return ""

    def focus_window(self, id):
        pass

    def translate_cmd(self, cmd):
        return ""

    def command(self, cmd):
        self.send_to_socket(cmd)
