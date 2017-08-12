import sys
from PyQt5.Qt import Qt, QApplication, QRectF
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene
from PyQt5.QtGui import QColor, QPainter

from thegame.gui.polygon import Polygon

class Scene(QGraphicsScene):
    def __init__(self):
        super().__init__()
        self.width = 5000
        self.height = 4000
        self.margin = 10
        self.initGame()

    def initGame(self):
        self.setSceneRect(5, 5, self.width, self.height)

        poly = Polygon(3)
        poly.setPos(100, 200)
        self.addItem(poly)
        poly.setVisible(True)
        print(666)

    def drawBackground(self, painter: QPainter, rect: QRectF):
        backgroundColor = QColor(10, 10, 255, 30)
        painter.setBrush(backgroundColor)
        painter.setPen(backgroundColor)
        for i in range(-5, self.width + 20, 20):
            painter.drawLine(i, 5, i, self.height + 5)
        for i in range(-5, self.height + 20, 20):
            painter.drawLine(5, i, self.width + 5, i)


class View(QGraphicsView):
    viewWidth = 960
    viewHeight = 768

    def __init__(self, scene):
        super().__init__(scene)
        self.resize(self.viewWidth, self.viewHeight)
        self.setWindowTitle('thegame')

        # The size of the view is not fixed. We may want to change it later
        self.setMinimumSize(self.viewWidth, self.viewHeight)
        self.setMaximumSize(self.viewWidth, self.viewHeight)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.centerOn(100, 200)


def main():
    global app
    app = QApplication(sys.argv)
    scene = Scene()
    view = View(scene)
    view.show()
    return app.exec()
