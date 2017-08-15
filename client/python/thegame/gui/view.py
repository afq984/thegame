from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeyEvent, QMouseEvent
from PyQt5.QtWidgets import QGraphicsView, QPushButton, QLabel, QButtonGroup

from thegame import Ability
from thegame.gui import const


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

        # so that mouseMoveEvent is always triggered
        self.setMouseTracking(True)

        self.keys = scene.keys

        self.initAbilityButtons()

    def initAbilityButtons(self):
        self.abilityButtons = []
        for ab in Ability:
            text = ab.as_camel.replace('_', ' ')
            label = QLabel(text, self)
            button = QPushButton('+', self)
            self.abilityButtons.append((label, button))
        self.abilityButtonGroup = QButtonGroup(self)
        for label, button in self.abilityButtons:
            label.setVisible(True)
            label.setEnabled(False)
            button.setVisible(True)
            button.setEnabled(False)
            self.abilityButtonGroup.addButton(button)
        self.setAbilityButtonStyle()

    def setAbilityButtonStyle(self):
        for i, (label, button) in enumerate(self.abilityButtons):
            label.setStyleSheet(const.AbilityLabelStyle)
            label.setAlignment(Qt.AlignCenter)
            if button.isEnabled():
                button.setStyleSheet(
                    const.AbilityButtonCommonStyle +
                    const.AbilityButtonEnabledStyleList)
            else:
                button.setStyleSheet(
                    const.AbilityButtonCommonStyle +
                    const.AbilityButtonDisabledStyle)

    def attachClient(self, client):
        self.rpc = client
        self.rpc.dataArrived.connect(self.updateDataSlot)

    def updateDataSlot(self):
        self.updateData(**self.rpc.data)

    def updateData(self, hero, heroes, polygons, bullets):
        for ab in Ability:
            self.abilityButtons[ab][0].setText(
                f'{ab.as_camel.replace("_", " ")} [{hero.abilities[ab].level}]'
            )

    def resizeEvent(self, event):
        currentWidth = self.width()
        currentHeight = self.height()
        for i, (label, button) in enumerate(self.abilityButtons):
            label.setGeometry(
                10,
                currentHeight - (8 - i) * const.AbilityYDelta - 10,
                const.AbilityLabelWidth,
                const.AbilityHeight,
            )
            button.setGeometry(
                const.AbilityLabelWidth + 10,
                currentHeight - (8 - i) * const.AbilityYDelta - 10,
                const.AbilityButtonWidth,
                const.AbilityHeight,
            )

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
        self.scene().mousePos = event.pos()

    def mousePressEvent(self, event):
        self.scene().mouseDown = True

    def mouseReleaseEvent(self, event):
        self.scene().mouseDown = False

    def wheelEvent(self, event):
        # consume the event so it will do nothing
        pass
