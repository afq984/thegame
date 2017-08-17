from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPen, QPainter, QColor, QBrush, QPainterPath, QFont
from PyQt5.QtWidgets import QWidget, QGraphicsObject, QStyleOptionGraphicsItem


class MessageDisplay(QGraphicsObject):
    def __init__(self):
        super().__init__()
        self.text = ''

    def boundingRect(self):
        return QRectF(-self.width, 0, self.width, self.height)

    def paint(
            self,
            painter: QPainter,
            option: QStyleOptionGraphicsItem,
            widget: QWidget):
        pen = QPen()
        pen.setWidth(1)
        painter.setRenderHint(QPainter.Antialiasing)
        pen.setColor(QColor(81, 81, 81, 255))
        painter.setPen(pen)
        painter.setBrush(QBrush(QColor(81, 81, 81, 255), Qt.SolidPattern))
        path = QPainterPath()
        path.addText(
            -self.width,
            self.height,
            QFont('monospace', 13, QFont.PreferNoHinting),
            self.text)
        painter.drawPath(path)

    def loadMessage(self, message):
        self.text = text
        self.update(self.boundingRect())
