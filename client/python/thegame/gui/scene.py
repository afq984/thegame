import itertools

from PyQt5.QtCore import Qt, QRect, QRectF, QPoint
from PyQt5.QtGui import QPainter, QColor, QBrush
from PyQt5.QtWidgets import QGraphicsScene

from thegame.gui.objecttracker import ObjectTracker
from thegame.gui.polygon import Polygon
from thegame.gui.hero import Hero
from thegame.gui.bullet import Bullet
from thegame.gui.experiencebar import ExperienceBar
from thegame.gui.scoreboard import Scoreboard


class Scene(QGraphicsScene):
    def __init__(self):
        super().__init__()
        self.width = 5000 + 1600
        self.height = 4000 + 1600
        self.margin = 10

        self.keys = {
            Qt.Key_W: False,
            Qt.Key_A: False,
            Qt.Key_S: False,
            Qt.Key_D: False,
        }  # This will be modified by View, and be read by GuiClient
        self.mouseDown = False
        self.mousePos = QPoint()
        self.decaying = []
        self.setSceneRect(5, 5, self.width, self.height)
        self.polygons = ObjectTracker()
        self.heroes = ObjectTracker()
        self.bullets = ObjectTracker()
        self.experienceBar = ExperienceBar()
        self.addItem(self.experienceBar)
        self.scoreboard = Scoreboard()
        self.addItem(self.scoreboard)

    def attachClient(self, client):
        self.rpc = client
        self.rpc.dataArrived.connect(self.updateDataSlot)

    def drawBackground(self, painter: QPainter, rect: QRectF):
        backgroundColor = QColor(10, 10, 255, 30)
        painter.setBrush(backgroundColor)
        painter.setPen(backgroundColor)
        for i in range(-5, self.width + 20 + 1, 20):
            painter.drawLine(i, 5, i, self.height + 5)
        for i in range(-5, self.height + 20 + 1, 20):
            painter.drawLine(5, i, self.width + 5, i)
        painter.fillRect(QRect(0, 0, 6600, 800), QBrush(QColor(0, 0, 0, 64)))
        painter.fillRect(QRect(0, 4800, 6600, 800), QBrush(QColor(0, 0, 0, 64)))
        painter.fillRect(QRect(0, 800, 800, 4000), QBrush(QColor(0, 0, 0, 64)))
        painter.fillRect(QRect(5800, 800, 800, 4000), QBrush(QColor(0, 0, 0, 64)))

    def updateDataSlot(self):
        self.updateData(**self.rpc.data)

    def updateData(self, hero, heroes, polygons, bullets):
        self.experienceBar.loadEntity(hero)

        for p in polygons:
            gp, created = self.polygons.get_or_create(p.id, Polygon, p.edges)
            if created:
                self.addItem(gp)
                self.addItem(gp.healthBar)
            gp.loadEntity(p)
        for b in bullets:
            gb, created = self.bullets.get_or_create(b.id, Bullet)
            if created:
                self.addItem(gb)
            gb.loadEntity(b)
        for h in itertools.chain([hero], heroes):
            gh, created = self.heroes.get_or_create(h.id, Hero)
            if created:
                self.addItem(gh)
                self.addItem(gh.healthBar)
                if h is hero:
                    gh.isSelf = True
            gh.loadEntity(h)

        for id, decay in itertools.chain(
            self.polygons.discard_reset(),
            self.bullets.discard_reset(),
            self.heroes.discard_reset(),
        ):
            if hasattr(decay, 'healthBar'):
                self.removeItem(decay.healthBar)
            self.decaying.append((id, decay))
        self.decaying = [
            tup for tup in self.decaying
            if not self.decay_and_remove(tup)
        ]

        view, = self.views()
        center_position = hero.position
        view.centerOn(center_position.x + 800, center_position.y + 800)
        self.setUiPos(view)

        # XXX this is ugly
        self.scoreboard.loadScores(self.rpc._game_state.meta.scores)

    def setUiPos(self, view):
        vw = view.width()
        vh = view.height()
        expCenter = view.mapToScene(
            QPoint(vw / 2, vh - 50))
        self.experienceBar.setPos(expCenter)
        scoreboardCenter = view.mapToScene(
            QPoint(vw - 5, 5))
        self.scoreboard.setPos(scoreboardCenter)

    def decay_and_remove(self, tup):
        '''
        return the opacity of the entity and return wheter the entity
        has been removed
        '''
        should_remove = self.decay(tup)
        id, entity = tup
        if should_remove:
            self.removeItem(entity)
        return should_remove

    def decay(self, tup):
        '''
        reduce the opacity of the entity and return whether the entity
        should be removed
        '''
        id, entity = tup
        if isinstance(entity, Hero) and id in self.heroes:
            return True
        if isinstance(entity, Bullet) and id in self.bullets:
            return True
        if isinstance(entity, Polygon) and id in self.polygons:
            return True
        opa = entity.opacity() - 0.1
        if opa <= 0:
            return True
        entity.setX(entity.x() + entity.velocity.x)
        entity.setY(entity.y() + entity.velocity.y)
        entity.setOpacity(opa)
        return False
