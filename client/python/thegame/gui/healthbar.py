from PyQt5.QtCore import QRectF, Qt
from PyQt5.QtGui import (
    QPainter, QPainterPath, QPen, QColor, QBrush
)
from PyQt5.QtWidgets import (
    QWidget, QGraphicsObject, QStyleOptionGraphicsItem
)

class HealthBar(QGraphicsObject):
    def __init__(self, initialHealth, width, offsetY):
        super().__init__()
        self.currentHealth = initialHealth
        self.maxHealth = initialHealth
        self.width = width
        self.offsetY = offsetY
        self.currentHealthWidth = width * (self.currentHealth / self.maxHealth)

    def boundingRect(self):
        penWidth = 3
        return QRectF(
            - self.width / 2 - penWidth,
            self.offsetY,
            self.width + penWidth,
            5 + penWidth
        )

    def paint(
            self,
            painter: QPainter,
            option: QStyleOptionGraphicsItem,
            widget: QWidget):
        pen = QPen()
        pen.setWidth(3)
        pen.setColor(QColor(85, 85, 85, 255))
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(pen)
        painter.setBrush(QBrush(QColor(85, 85, 85, 255), Qt.SolidPattern))
        painter.drawRect(-self.width / 2, self.offsetY, self.width, 6)
        painter.setBrush(QBrush(QColor(134, 198, 128, 255), Qt.SolidPattern))
        painter.drawRect(-self.width / 2, self.offsetY, self.currentHealthWidth, 6)

    def shape(self):
        path = QPainterPath()
        path.addEllipse(
            -self.width / 2, self.offsetY, self.currentHealthWidth, 6)
        path.addEllipse(
            -self.width / 2, self.offsetY, self.width, 6
        )
        return path

    def setHealth(self, currentHealth, maxHealth):
        self.currentHealth = currentHealth
        self.maxHealth = maxHealth
        self.currentHealthWidth = self.width * currentHealth / maxHealth
        self.update(self.boundingRect())
