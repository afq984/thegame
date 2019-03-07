from PyQt5.QtWidgets import (
    QDialog, QLabel, QDialogButtonBox, QVBoxLayout, QLineEdit)

import grpc

from thegame.gui import GuiClient
from thegame import thegame_pb2, thegame_pb2_grpc


class AudienceClient(GuiClient):

    def init(self):
        self.to_level_up = []
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
        self.token = line.text()

    def run(self):
        self._parse()
        remote = self.remote
        channel = grpc.insecure_channel(remote)
        stub = thegame_pb2_grpc.TheGameStub(channel)
        for response in stub.View(thegame_pb2.ViewRequest(token=self.token)):
            self._game_state = response
            self._response_to_controls(response)


if __name__ == '__main__':
    AudienceClient.main()
