from thegame.gui import GuiClient


class InteractiveClient(GuiClient):

    def action(self, **kwds):
        x = y = 0
        if self.scene.keys[Qt.Key_W]:
            y -= 1
        if self.scene.keys[Qt.Key_A]:
            x -= 1
        if self.scene.keys[Qt.Key_S]:
            y += 1
        if self.scene.keys[Qt.Key_D]:
            x += 1
        if x or y:
            self.accelerate(math.atan2(y, x))
        mpos = self.scene.views()[0].mapToScene(self.scene.mousePos)
        self.shoot_at(
            mpos.x(), mpos.y(),
            rotate_only=not self.scene.mouseDown)
