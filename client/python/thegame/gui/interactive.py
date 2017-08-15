import math

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QAbstractButton

from thegame.gui import GuiClient


class InteractiveClient(GuiClient):

    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        self.to_level_up = []

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
            mpos.x(), mpos.y(),
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
