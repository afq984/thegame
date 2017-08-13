import math
import random

from PyQt5.QtCore import QPoint, QRectF, QTimer
from PyQt5.QtGui import (
    QPainter, QPainterPath, QPen, QColor, QBrush, QPolygonF
)
from PyQt5.QtWidgets import (
    QWidget, QGraphicsObject, QStyleOptionGraphicsItem
)
from thegame.gui.healthbar import HealthBar


class Polygon(QGraphicsObject):

    def __init__(self, edges):
        super().__init__()
        self.axis = 20
        self.healthBar = HealthBar(1000, 2 * self.axis, self.axis + 5)
        self.edges = edges
        self.constructPolygon()

        self.rotationAngle = random.random() - 0.5
        self.rotationTimer = QTimer(self)
        self.rotationTimer.timeout.connect(self.rotate)
        self.rotationTimer.start(25)

    def loadEntity(self, entity):
        self.setPos(*entity.position)
        self.healthBar.setPos(*entity.position)
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
        pen = QPen()
        pen.setWidth(3)
        pen.setColor(QColor(85, 85, 85, 255))
        painter.setPen(pen)
        brushColor = {
            3: QColor(252, 118, 119, 255),
            4: QColor(255, 232, 105, 255),
            5: QColor(118, 141, 252, 255),
        }[self.edges]
        painter.setBrush(QBrush(brushColor))
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
