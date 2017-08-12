import sys
from PyQt5.Qt import Qt, QApplication, QRectF
from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene
from PyQt5.QtGui import QColor, QPainter
import grpc
import threading

from thegame import thegame_pb2, thegame_pb2_grpc
from thegame.entity import Debris
from thegame.gui.polygon import Polygon

def emptyg():
    import time
    time.sleep(10)
    yield 3

class Scene(QGraphicsScene):
    def __init__(self):
        super().__init__()
        self.width = 5000
        self.height = 4000
        self.margin = 10
        self.initGame()

    def initGame(self):
        self.setSceneRect(5, 5, self.width, self.height)
        self.polygons = {}
        self.wow()
        class T(QThread):
            def run(se1f):
                self.wow()
        t = T()
        # threading.Thread(target=self.wow).start()

    def drawBackground(self, painter: QPainter, rect: QRectF):
        backgroundColor = QColor(10, 10, 255, 30)
        painter.setBrush(backgroundColor)
        painter.setPen(backgroundColor)
        for i in range(-5, self.width + 20, 20):
            painter.drawLine(i, 5, i, self.height + 5)
        for i in range(-5, self.height + 20, 20):
            painter.drawLine(5, i, self.width + 5, i)


    def dataArrived(self, debris):
        for id, d in enumerate(debris):
            try:
                poly = self.polygons[id]
            except KeyError:
                poly = self.polygons[id] = Polygon(d.edges)
                self.addItem(poly)
            poly.setPos(*d.position)

    def wow(self):
        channel = grpc.insecure_channel('localhost:50051')
        stub = thegame_pb2_grpc.TheGameStub(channel)
        for response in stub.Game(emptyg()):
            debris = [Debris(d) for d in response.debris]
            self.dataArrived(debris)
            break

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
