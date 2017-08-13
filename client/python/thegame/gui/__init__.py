import sys

from PyQt5.QtWidgets import QApplication

from thegame.gui.scene import Scene
from thegame.gui.view import View


app = None


def main():
    global app
    app = QApplication(sys.argv)
    scene = Scene()
    view = View(scene)
    view.show()
    return app.exec()
