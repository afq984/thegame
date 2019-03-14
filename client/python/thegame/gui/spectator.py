from PyQt5.QtWidgets import (
    QDialog, QLabel, QDialogButtonBox, QVBoxLayout, QLineEdit)

import grpc
import queue
import time
import threading
from thegame.gui import GuiClient
from thegame import thegame_pb2, thegame_pb2_grpc
from thegame.api import GameState


class SpectatorClient(GuiClient):

    def _action(self, **kwds):
        if self.options.smooth:
            self.frames.put(kwds)
        else:
            super()._action(**kwds)

    def _consumer(self):
        fps = 40

        qsize0 = self.frames.qsize()
        while True:
            kwds = self.frames.get()
            super()._action(**kwds)
            time.sleep(1 / fps)
            qsize1 = self.frames.qsize()
            fps *= 0.999 + (qsize1 - qsize0 + 1) * 0.001
            print('est. fps:', fps, 'stored:', qsize1)
            qsize0 = qsize1

    def init(self):
        self.to_level_up = []

    @staticmethod
    def get_token():
        dialog = QDialog()
        layout = QVBoxLayout()
        layout.addWidget(QLabel('Enter server token:'))
        line = QLineEdit()
        layout.addWidget(line)
        box = QDialogButtonBox()
        button = box.addButton('OK', QDialogButtonBox.AcceptRole)
        button.clicked.connect(dialog.accept)
        layout.addWidget(box)
        dialog.setLayout(layout)
        dialog.exec()
        return line.text()

    @classmethod
    def _configure_parser(cls, parser):
        super()._configure_parser(parser)
        parser.add_argument('--token', default='')
        parser.add_argument('--smooth', action='store_true')

    def run(self):
        remote = self.options.remote
        token = self.options.token

        if self.options.smooth:
            self.frames = queue.Queue()
            self.play_thread = threading.Thread(target=self._consumer, daemon=True)
            self.play_thread.start()

        channel = grpc.insecure_channel(remote)
        stub = thegame_pb2_grpc.TheGameStub(channel)
        for response in stub.View(thegame_pb2.ViewRequest(token=token)):
            self._game_state = response
            self._game_state_to_controls(GameState(response))


if __name__ == '__main__':
    SpectatorClient.main()
