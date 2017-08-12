import math

from PyQt5.QtCore import QPoint, QRectF
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
        for i in range(self.edges):
            theta = math.tau * i / self.edges
            points.append(QPoint(
                self.axis * math.cos(theta),
                self.axis * math.sin(theta)
            ))
        points.append(QPoint(self.axis, 0))
        print(points)
        self.polygonShape = QPolygonF(points)
