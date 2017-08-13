import collections
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
        x, y = kwds['hero'].position
        if self.scene.keys[Qt.Key_W]:
            y -= 1
        if self.scene.keys[Qt.Key_A]:
            x -= 1
        if self.scene.keys[Qt.Key_S]:
            y += 1
        if self.scene.keys[Qt.Key_D]:
            x += 1
        self.accelerate(x, y)
        mpos = self.scene.views()[0].mapToScene(self.scene.mousePos)
        self.shoot(mpos.x(), mpos.y(), not self.scene.mouseDown)
