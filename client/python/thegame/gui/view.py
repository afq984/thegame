from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeyEvent, QMouseEvent
from PyQt5.QtWidgets import QGraphicsView


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

        self.keys = scene.keys

    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()
        if key in self.keys:
            self.keys[key] = True

    def keyReleaseEvent(self, event: QKeyEvent):
        if event.isAutoRepeat():
            event.ignore()
            return
        key = event.key()
        if key in self.keys:
            self.keys[key] = False

    def mouseMoveEvent(self, event: QMouseEvent):
        point = self.mapToScene(event.pos())
        self.scene().mouseLocation = (point.x(), point.y())

    def mousePressEvent(self, event):
        self.scene().mouseDown = True

    def mouseReleaseEvent(self, event):
        self.scene().mouseDown = False

    def wheelEvent(self, event):
        # consume the event so it will do nothing
        pass
