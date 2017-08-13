import sys
import collections
from PyQt5.Qt import Qt, QApplication, QRectF
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene
from PyQt5.QtGui import QColor, QPainter, QKeyEvent

from thegame.api import Client
from thegame.gui.polygon import Polygon
from thegame.gui.hero import Hero


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


class Scene(QGraphicsScene):
    def __init__(self):
        super().__init__()
        self.width = 5000
        self.height = 4000
        self.margin = 10

        self.keys = {
            Qt.Key_W: False,
            Qt.Key_A: False,
            Qt.Key_S: False,
            Qt.Key_D: False,
        }  # This will be modified by View, and be read by GuiClient

        self.initGame()

    def initGame(self):
        self.setSceneRect(5, 5, self.width, self.height)
        self.polygons = {}
        self.heroes = {}
        self.rpc = GuiClient(self)
        self.rpc.dataArrived.connect(self.updateDataSlot)
        self.rpc.start()

    def drawBackground(self, painter: QPainter, rect: QRectF):
        backgroundColor = QColor(10, 10, 255, 30)
        painter.setBrush(backgroundColor)
        painter.setPen(backgroundColor)
        for i in range(-5, self.width + 20, 20):
            painter.drawLine(i, 5, i, self.height + 5)
        for i in range(-5, self.height + 20, 20):
            painter.drawLine(5, i, self.width + 5, i)

    def updateDataSlot(self):
        self.updateData(**self.rpc.dataQueue.popleft())

    def updateData(self, hero, heroes, polygons, bullets):
        for d in polygons:
            try:
                poly = self.polygons[d.id]
            except KeyError:
                poly = self.polygons[d.id] = Polygon(d.edges)
                self.addItem(poly)
            poly.setPos(*d.position)
        for h in heroes:
            try:
                hr = self.heroes[h.id]
            except KeyError:
                hr = self.polygons[h.id] = Hero()
                self.addItem(hr)
            hr.setPos(*h.position)

        for view in self.views():
            view.centerOn(*hero.position)


class View(QGraphicsView):
    viewWidth = 960
    viewHeight = 768

    def __init__(self, scene):
        super().__init__(scene)
        self.resize(self.viewWidth, self.viewHeight)
        self.setWindowTitle('thegame')

        # The size of the view is not fixed. We may want to change it later
        self.setMinimumSize(self.viewWidth, self.viewHeight)
        self.setMaximumSize(self.viewWidth, self.viewHeight)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.centerOn(100, 200)

        self.keys = scene.keys

    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()
        if key in self.keys:
            self.keys[key] = True

    def keyReleaseEvent(self, event: QKeyEvent):
        if event.isAutoRepeat():
            event.ignore()
            return
        key = event.key()
        if key in self.keys:
            self.keys[key] = False


def main():
    global app
    app = QApplication(sys.argv)
    scene = Scene()
    view = View(scene)
    view.show()
    return app.exec()
