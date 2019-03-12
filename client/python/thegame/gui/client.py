from PyQt5.QtCore import QThread, pyqtSignal

from thegame import HeadlessClient
import copy


class GuiClient(HeadlessClient, QThread):
    '''
    GUI Client to be used with thegame.gui.view.View and thegame.gui.view.Scene
    '''

    dataArrived = pyqtSignal()

    def _action(self, **kwds):
        self.action(**copy.deepcopy(kwds))
        self.data = kwds
        self.dataArrived.emit()

    def _attach(self, view, scene):
        '''attach to view and scene'''
        self.scene = scene
        self.view = view
        scene.attachClient(self)
        view.attachClient(self)

    @classmethod
    def main(cls):
        from thegame.gui import main
        main(cls)
