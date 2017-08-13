from PyQt5.QtCore import QPointF, QRectF, Qt
from PyQt5.QtGui import (
    QPainter, QPainterPath, QPen, QColor, QBrush, QPolygonF
)
from PyQt5.QtWidgets import (
    QWidget, QGraphicsObject, QStyleOptionGraphicsItem
)
from thegame.gui.healthbar import HealthBar


class Bullet(QGraphicsObject):
    def __init__(self):
        super().__init__()
        self.radius = 10

    def boundingRect(self):
        halfPenWidth = 2
        return QRectF(
            -self.radius - halfPenWidth,
            -self.radius - halfPenWidth,
            self.radius * 2 + halfPenWidth,
            self.radius * 2 + halfPenWidth,
        )

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionGraphicsItem,
        widget: QWidget,
    ):
        pen = QPen()
        pen.setWidth(4)
        pen.setColor(QColor(85, 85, 85, 255))
        painter.setPen(pen)
        painter.setBrush(QBrush(QColor(241, 78, 84, 255), Qt.SolidPattern))
        painter.setRenderHint(QPainter.Antialiasing)
        painter.drawPath(self.shape())

    def shape(self):
        path = QPainterPath()
        path.addEllipse(
            -self.radius, -self.radius, self.radius * 2, self.radius * 2)
        return path
