from PyQt5.QtCore import QRectF, Qt
from PyQt5.QtGui import (
    QPainter, QPainterPath, QPen, QColor, QBrush
)
from PyQt5.QtWidgets import (
    QWidget, QGraphicsObject, QStyleOptionGraphicsItem
)

from thegame.gui import const


class Bullet(QGraphicsObject):
    def __init__(self):
        super().__init__()
        self.radius = 10
        self.setZValue(8)

    def loadEntity(self, entity):
        self.setPos(entity.position.x + 800, entity.position.y + 800)
        self.velocity = entity.velocity

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
        painter.setPen(const.FramePen)
        painter.setBrush(const.BulletBrush)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.drawPath(self.shape())

    def shape(self):
        path = QPainterPath()
        path.addEllipse(
            -self.radius, -self.radius, self.radius * 2, self.radius * 2)
        return path
