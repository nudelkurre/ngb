class WindowManagerIPC:
    def __init__(self):
        pass

    def send_to_socket(self, cmd):
        pass

    def parse_workspace(self, ws):
        return []

    def get_workspaces(self):
        return []

    def translate_cmd(self, cmd):
        return ""

    def command(self, cmd):
        self.send_to_socket(cmd)