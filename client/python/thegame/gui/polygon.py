import math
import random

from PyQt5.QtCore import QPoint, QRectF, QTimer
from PyQt5.QtGui import (
    QPainter, QPainterPath, QPen, QColor, QBrush, QPolygonF
)
from PyQt5.QtWidgets import (
    QWidget, QGraphicsObject, QStyleOptionGraphicsItem
)
from thegame.gui import const
from thegame.gui.healthbar import HealthBar


class Polygon(QGraphicsObject):

    def __init__(self, edges):
        super().__init__()
        if edges == 5:
            self.axis = 25
        else:
            self.axis = 20
        self.healthBar = HealthBar(1000, 2 * self.axis, self.axis + 5)
        self.edges = edges
        self.constructPolygon()

        self.setRotation(random.random() * 360)

        self.rotationAngle = random.random() * 2 - 1
        self.rotationTimer = QTimer(self)
        self.rotationTimer.timeout.connect(self.rotate)
        self.rotationTimer.start(25)
        self.setZValue(1)

    def loadEntity(self, entity):
        self.setPos(entity.position.x + 800, entity.position.y + 800)
        self.healthBar.setPos(entity.position.x + 800, entity.position.y + 800)
        self.healthBar.setHealth(entity.health, entity.max_health)
        self.velocity = entity.velocity

    def rotate(self):
        self.setRotation(self.rotation() + self.rotationAngle)

    def paint(
            self,
            painter: QPainter,
            option: QStyleOptionGraphicsItem,
            widget: QWidget,
            ):
        painter.setPen(const.FramePen)
        painter.setBrush(const.PolygonBrushes[self.edges])
        painter.setRenderHint(QPainter.Antialiasing)
        painter.drawPath(self.shape())

    def shape(self):
        path = QPainterPath()
        path.addPolygon(self.polygonShape)
        return path

    def boundingRect(self):
        halfPenWidth = 1.5
        return QRectF(
            -self.axis - halfPenWidth,
            -self.axis - halfPenWidth,
            self.axis * 2 + halfPenWidth,
            self.axis * 2 + halfPenWidth,
        )

    def constructPolygon(self):
        points = []
        rbase = math.tau / self.edges
        for i in range(self.edges):
            theta = i * rbase
            points.append(QPoint(
                self.axis * math.cos(theta),
                self.axis * math.sin(theta)
            ))
        points.append(QPoint(self.axis, 0))
        self.polygonShape = QPolygonF(points)
