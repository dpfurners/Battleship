"""
This File contains the logic of the server.

It connects the server network, the database interface and provides to logic to play the game.
"""
import threading

from server.network.interface import NetworkServerWithLobby
from server.database import DBInterface


class ServerLogic:
    def __init__(self, host: str = "localhost", port: int = 1234):
        self.db = DBInterface()
        self.network = NetworkServerWithLobby(host, port, self.db)

        self.accept_thread = threading.Thread(target=self.network.accept_new)

    def run(self):
        self.accept_thread.start()
        try:
            while True:
                pass
        except KeyboardInterrupt:
            self.close()

    def close(self):
        self.network.close()
        self.db.Close()
