from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeyEvent, QMouseEvent
from PyQt5.QtWidgets import QGraphicsView, QPushButton, QLabel, QButtonGroup

from thegame import Ability
from thegame.gui import const


class View(QGraphicsView):
    viewWidth = 1280
    viewHeight = 768

    def __init__(self, scene):
        super().__init__(scene)
        self.resize(self.viewWidth, self.viewHeight)
        self.setWindowTitle('thegame')

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # so that mouseMoveEvent is always triggered
        self.setMouseTracking(True)

        self.keys = scene.keys

        self.initAbilityButtons()

    def initAbilityButtons(self):
        self.abilityButtons = []
        self.abilityButtonGroup = QButtonGroup(self)
        for ab in Ability:
            text = ab.as_camel.replace('_', ' ')
            label = QLabel(text, self)
            button = QPushButton('+', self)
            self.abilityButtons.append((label, button))
            label.setVisible(True)
            label.setEnabled(False)
            button.setVisible(True)
            button.setEnabled(False)
            self.abilityButtonGroup.addButton(button, ab)
        self.setAbilityButtonStyle()

    def setAbilityButtonStyle(self):
        for i, (label, button) in enumerate(self.abilityButtons):
            label.setStyleSheet(const.AbilityLabelStyle)
            label.setAlignment(Qt.AlignCenter)
            if button.isEnabled():
                button.setStyleSheet(
                    const.AbilityButtonCommonStyle +
                    const.AbilityButtonEnabledStyleList[i])
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
        for ab, (label, button) in zip(Ability, self.abilityButtons):
            self.abilityButtons[ab][0].setText(
                f'{ab.as_camel.replace("_", " ")} [{hero.abilities[ab].level}]'
            )
            button.setEnabled(
                hero.skill_points > 0
                and hero.abilities[ab].level < 8)
        self.setAbilityButtonStyle()

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
        self.scene().setUiPos(self)

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
