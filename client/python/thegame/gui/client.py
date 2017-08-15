import collections
from PyQt5.QtCore import QThread, pyqtSignal

from thegame import HeadlessClient


class GuiClient(HeadlessClient, QThread):
    '''
    GUI Client to be used with thegame.gui.view.View and thegame.gui.view.Scene
    '''

    dataArrived = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.dataQueue = collections.deque()

    def _action(self, **kwds):
        self.action(**kwds)
        self.dataQueue.append(kwds)
        self.dataArrived.emit()

    def _attach(self, view, scene):
        '''attach to view and scene'''
        self.scene = scene
        self.view = view
        scene.attachClient(self)
        view.attachClient(self)

    def run(self):
        self._parse()
        super().run()

    @classmethod
    def main(cls):
        from thegame.gui import main
        self = cls()
        self._parse()
        main(self)
