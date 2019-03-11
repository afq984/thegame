import math

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QAbstractButton, QDialog, QLabel, QPushButton,
    QDialogButtonBox, QVBoxLayout, QLineEdit)

from thegame.gui import GuiClient


class InteractiveClient(GuiClient):

    def init(self):
        self.to_level_up = []
        dialog = QDialog()
        layout = QVBoxLayout()
        layout.addWidget(QLabel('Enter your name:'))
        line = QLineEdit()
        layout.addWidget(line)
        box = QDialogButtonBox()
        button = box.addButton('OK', QDialogButtonBox.AcceptRole)
        button.clicked.connect(dialog.accept)
        layout.addWidget(box)
        dialog.setLayout(layout)
        dialog.exec()
        self.name = line.text()

    def action(self, **kwds):
        x = y = 0
        if self.scene.keys[Qt.Key_W]:
            y -= 1
        if self.scene.keys[Qt.Key_A]:
            x -= 1
        if self.scene.keys[Qt.Key_S]:
            y += 1
        if self.scene.keys[Qt.Key_D]:
            x += 1
        if x or y:
            self.accelerate(math.atan2(y, x))
        mpos = self.scene.views()[0].mapToScene(self.scene.mousePos)
        self.shoot_at(
            mpos.x() - 800, mpos.y() - 800,
            rotate_only=not self.scene.mouseDown)
        try:
            while True:
                self.level_up(self.to_level_up.pop())
        except IndexError:
            pass

    def add_level_up(self, ab):
        self.to_level_up.append(ab)

    def _attach(self, view, scene):
        super()._attach(view, scene)
        view.abilityButtonGroup.buttonClicked[int].connect(self.add_level_up)
