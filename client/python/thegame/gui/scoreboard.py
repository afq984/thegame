from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPen, QPainter, QColor, QBrush, QPainterPath, QFont
from PyQt5.QtWidgets import QWidget, QGraphicsObject, QStyleOptionGraphicsItem


class Scoreboard(QGraphicsObject):
    def __init__(self):
        super().__init__()
        self.width = 250
        self.scores = []
        self.setZValue(10)

    @property
    def height(self):
        return len(self.scores) * 16

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
        for i, score in enumerate(self.scores):
            path = QPainterPath()
            path.addText(
                -self.width,
                14 + i * 16,
                QFont('monospace', 13, QFont.PreferNoHinting),
                f'{score.score:6}[{score.level:2}]  {score.hero_name}')
            painter.drawPath(path)

    def loadScores(self, scores):
        self.scores = scores
        self.update(self.boundingRect())
