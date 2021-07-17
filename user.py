import random


class User:
    def __init__(self, CLIENT_SOCKET, ADDRESS):
        self.CLIENT_SOCKET = CLIENT_SOCKET
        self.ADDRESS = ADDRESS
        self.name = None
        self.identifier = random.random()*(10**16)

    def __repr__(self):
        return f"<{self.CLIENT_SOCKET}> IP({self.ADDRESS})"

    def __eq__(self, other):
        return self.identifier == other.identifier

    def set_name(self, name):
        self.name = name
