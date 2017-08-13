from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtWidgets import QGraphicsScene

from thegame.gui.client import GuiClient
from thegame.gui.objecttracker import ObjectTracker
from thegame.gui.polygon import Polygon
from thegame.gui.hero import Hero


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
        self.mouseDown = False
        self.mouseLocation = (0, 0)

        self.initGame()

    def initGame(self):
        self.setSceneRect(5, 5, self.width, self.height)
        self.polygons = ObjectTracker()
        self.heroes = ObjectTracker()
        self.bullets = ObjectTracker()
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
        for p in polygons:
            gp, created = self.polygons.get_or_create(p.id, Polygon, p.edges)
            if created:
                self.addItem(gp)
            gp.setPos(*p.position)
        for h in heroes:
            gh, created = self.heroes.get_or_create(h.id, Hero)
            if created:
                self.addItem(gh)
            gh.setPos(*h.position)

        for view in self.views():
            view.centerOn(*hero.position)
