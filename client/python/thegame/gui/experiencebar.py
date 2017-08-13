from PyQt5.QtCore import Qt, QTimer, QRectF
from PyQt5.QtGui import QPen, QPainter, QColor, QBrush
from PyQt5.QtWidgets import QWidget, QGraphicsObject, QStyleOptionGraphicsItem


class ExperienceBar(QGraphicsObject):
    def __init__(self):
        super().__init__()
        self.name = '<UNKNOWN NAME>'
        self.level = 1
        self.actualExperience = 0
        self.maxExperience = 1
        self.maxWidth = 500
        self.displayWidth = 0
        self.setOpacity(0.8)
        self.setZValue(1)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.stepExperience)
        self.timer.start(25)

    def boundingRect(self):
        return QRectF(-self.maxWidth / 2, -15, self.maxWidth, 30)

    @property
    def actualWidth(self):
        return int(
            self.maxWidth * self.actualExperience / self.maxExperience
        )

    def paint(
            self,
            painter: QPainter,
            option: QStyleOptionGraphicsItem,
            widget: QWidget):
        pen = QPen()
        pen.setWidth(3)
        painter.setRenderHint(QPainter.Antialiasing)
        pen.setColor(QColor(61, 61, 61, 255))
        painter.setPen(pen)
        painter.setBrush(QBrush(QColor(61, 61, 61, 255), Qt.SolidPattern))
        painter.drawRect(
            QRectF(-self.maxWidth / 2, -10, self.maxWidth, 20))
        painter.setBrush(QBrush(QColor(240, 217, 108, 255), Qt.SolidPattern))
        painter.drawRect(
            QRectF(-self.maxWidth / 2, -10, self.displayWidth, 20))

    def stepExperience(self):
        if self.displayWidth == self.actualWidth:
            return
        difference = self.actualWidth - self.displayWidth
        if self.displayWidth < self.actualWidth:
            self.displayWidth += difference // 30 + 1
        else:
            self.displayWidth += difference // 30 - 1
        self.update(self.boundingRect())

    def loadEntity(self, hero):
        self.actualExperience = hero.experience
        self.maxExperience = hero.experience_to_level_up
