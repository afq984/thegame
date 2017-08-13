import math

from PyQt5.QtCore import QPointF, QRectF
from PyQt5.QtGui import (
    QPainter, QPainterPath, QPen, QColor, QBrush, QPolygonF
)
from PyQt5.QtWidgets import (
    QWidget, QGraphicsObject, QStyleOptionGraphicsItem
)
from thegame.gui.healthbar import HealthBar


class Hero(QGraphicsObject):
    def __init__(self):
        super().__init__()
        self.width = 60

        # XXX what does this do?
        self.setFlags(QGraphicsObject.ItemIsFocusable)

        radian60 = math.radians(30)
        shapePoint = [
            QPointF(
                math.cos(radian60) * self.width / 2 + 3,
                -math.sin(radian60) * self.width / 2),
            QPointF(
                math.cos(radian60) * self.width / 2 + 30,
                -math.sin(radian60) * self.width / 2),
            QPointF(
                math.cos(radian60) * self.width / 2 + 30,
                math.sin(radian60) * self.width / 2),
            QPointF(
                math.cos(radian60) * self.width / 2 + 3,
                math.sin(radian60) * self.width / 2),
        ]
        self.barrel = QPolygonF(shapePoint)

        self.healthBar = HealthBar(10000, 60, 40)

