from PyQt5.QtCore import QRectF, Qt
from PyQt5.QtGui import (
    QPainter, QPainterPath, QPen, QColor, QBrush
)
from PyQt5.QtWidgets import (
    QWidget, QGraphicsObject, QStyleOptionGraphicsItem
)

from thegame.gui import const


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
        painter.setPen(const.FramePen)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(const.HealthBarBackgroundBrush)
        painter.drawRect(-self.width / 2, self.offsetY, self.width, self.height)
        painter.setBrush(const.HealthBarForegroundBrush)
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
        currentHealth = max(currentHealth, 0)
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

        painter.setPen(const.HeroNamePen)
        painter.setRenderHint(QPainter.Antialiasing)
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
