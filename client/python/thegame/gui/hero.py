import math

from PyQt5.QtCore import QPointF, QRectF, Qt
from PyQt5.QtGui import (
    QPainter, QPainterPath, QPen, QColor, QBrush, QPolygonF
)
from PyQt5.QtWidgets import (
    QWidget, QGraphicsObject, QStyleOptionGraphicsItem
)
from thegame.gui.healthbar import NamedHealthBar
from thegame.gui import const


class Hero(QGraphicsObject):
    def __init__(self):
        super().__init__()
        self.width = 60

        # XXX what does this do?
        self.setFlags(QGraphicsObject.ItemIsFocusable)

        radian60 = math.radians(30)
        shapePoint = [
            QPointF(
                math.cos(radian60) * self.width / 2,
                -math.sin(radian60) * self.width / 2),
            QPointF(
                math.cos(radian60) * self.width / 2 + 30,
                -math.sin(radian60) * self.width / 2),
            QPointF(
                math.cos(radian60) * self.width / 2 + 30,
                math.sin(radian60) * self.width / 2),
            QPointF(
                math.cos(radian60) * self.width / 2,
                math.sin(radian60) * self.width / 2),
        ]
        self.barrel = QPolygonF(shapePoint)

        self.healthBar = NamedHealthBar(10000, 60, 40)
        self.setZValue(0)

        self.isSelf = False

    def loadEntity(self, entity):
        self.healthBar.setName(entity.name)
        self.setPos(entity.position.x + 800, entity.position.y + 800)
        self.setRotation(math.degrees(entity.orientation))
        self.healthBar.setPos(entity.position.x + 800, entity.position.y + 800)
        self.healthBar.setHealth(entity.health, entity.max_health)
        self.velocity = entity.velocity

    def boundingRect(self):
        halfPenWidth = 3 / 2
        return QRectF(
            -self.width - halfPenWidth,
            -self.width - halfPenWidth,
            self.width * 2 + 2 * halfPenWidth,
            self.width * 2 + 2 * halfPenWidth,
        )

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionGraphicsItem,
        widget: QWidget,
    ):
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(const.FramePen)
        painter.setBrush(const.HeroBarrelBrush)
        painter.drawPolygon(self.barrel)
        painter.setBrush(const.HeroBrush)
        if not self.isSelf:
            painter.setBrush(QBrush(QColor(0, 178, 255, 255), Qt.SolidPattern))
        else:
            painter.setBrush(QBrush(QColor(54, 212, 131, 255), Qt.SolidPattern))
        painter.drawEllipse(
            -self.width / 2, -self.width / 2, self.width, self.width)

    def shape(self):
        path = QPainterPath()
        path.addPolygon(self.barrel)
        path.addEllipse(
            -self.width / 2, -self.width / 2, self.width, self.width)
        return path
