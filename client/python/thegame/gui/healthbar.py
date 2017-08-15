from PyQt5.QtCore import QRectF, Qt
from PyQt5.QtGui import (
    QPainter, QPainterPath, QPen, QColor, QBrush
)
from PyQt5.QtWidgets import (
    QWidget, QGraphicsObject, QStyleOptionGraphicsItem
)


class HealthBar(QGraphicsObject):
    height = 6

    def __init__(self, initialHealth, width, offsetY):
        super().__init__()
        self.currentHealth = initialHealth
        self.maxHealth = initialHealth
        self.width = width
        self.offsetY = offsetY
        self.currentHealthWidth = width * (self.currentHealth / self.maxHealth)
        self.setZValue(9)

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
        painter.drawRect(-self.width / 2, self.offsetY, self.width, self.height)
        painter.setBrush(QBrush(QColor(134, 198, 128, 255), Qt.SolidPattern))
        painter.drawRect(-self.width / 2, self.offsetY, self.currentHealthWidth, self.height)

    def shape(self):
        path = QPainterPath()
        path.addEllipse(
            -self.width / 2, self.offsetY, self.currentHealthWidth, 6)
        path.addEllipse(
            -self.width / 2, self.offsetY, self.width, 6
        )
        return path

    def setHealth(self, currentHealth, maxHealth, alwaysVisible=False):
        self.currentHealth = currentHealth
        self.maxHealth = maxHealth
        self.currentHealthWidth = self.width * currentHealth / maxHealth
        self.setVisible(
            alwaysVisible or
            self.currentHealth != self.maxHealth)
        self.update(self.boundingRect())


class NamedHealthBar(HealthBar):
    '''
    A health bar with a name (of a Hero)
    '''
    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        self.name = 'UNKNOWN'

    def setName(self, name):
        self.name = name

    def boundingRect(self):
        penWidth = 3
        return QRectF(
            - self.width / 2 - penWidth - 15,
            - self.offsetY - 14,
            self.width + penWidth * 2 + 30,
            19 + penWidth + self.offsetY * 2
        )

    def paint(
            self,
            painter: QPainter,
            option: QStyleOptionGraphicsItem,
            widget: QWidget):
        super().paint(painter, option, widget)
        pen = QPen()
        pen.setWidth(3)
        pen.setColor(QColor(84, 84, 84, 255))
        painter.setPen(pen)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(QColor(240, 240, 240, 255), Qt.SolidPattern))
        painter.drawText(
            QRectF(
                -self.width / 2 - 15,
                -self.offsetY - 14,
                self.width + 30,
                14),
            Qt.AlignCenter,
            self.name)

    def setHealth(self, currentHealth, maxHealth):
        super().setHealth(currentHealth, maxHealth, True)
