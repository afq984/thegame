import collections
import math
from PyQt5.QtCore import Qt, QThread, pyqtSignal

from thegame import Client


class GuiClient(Client, QThread):

    dataArrived = pyqtSignal()

    def __init__(self, scene):
        super().__init__()
        self.dataQueue = collections.deque()
        self.scene = scene

    def action(self, **kwds):
        self.dataQueue.append(kwds)
        self.dataArrived.emit()
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
