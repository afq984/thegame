from thegame.gui.client import GuiClient


__all__ = ('GuiClient',)


app = None


def main(client_instance=None):
    global app
    if client_instance is None:
        from thegame.gui.interactive import InteractiveClient
        client_instance = InteractiveClient()
    import sys
    from PyQt5.QtWidgets import QApplication
    from thegame.gui.scene import Scene
    from thegame.gui.view import View

    app = QApplication(sys.argv)
    scene = Scene(client_instance=client_instance)
    view = View(scene)
    view.show()
    return app.exec()
