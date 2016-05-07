import pygame
import gui
import numpy as np

import sectors

LEFT = 0
RIGHT = 1
class Menu:
    def __init__(self, ui):
        self.ui = ui
        self.currentPane = LEFT
        self.currentItem = [None, None]
        self.menu = None
        self.model = None
        self.rightPanes = {}
        self.leftButtons = {}
        self.rightButtons = {}

    def actionPerformed(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP or event.key == pygame.K_LEFT:
                self.moveCursorUp()
            elif event.key == pygame.K_DOWN or event.key == pygame.K_RIGHT:
                self.moveCursorDown()
            elif event.key == pygame.K_RETURN:
                if self.currentPane == LEFT:
                    self.currentPane = RIGHT
                    self.currentItem[RIGHT] = self.model.defaultRightItem()
                    self.rightButtons[self.currentRightKey()].active = True
            elif event.key == pygame.K_ESCAPE:
                if self.currentPane == RIGHT:
                    self.currentPane = LEFT
                    self.rightButtons[self.currentRightKey()].active = False
                    self.currentItem[RIGHT] = None
                else:
                    self.leftButtons[self.currentItem[LEFT]].active = False
                    return 'game'
        return 'menu'

    def currentRightKey(self):
        return str(self.currentItem[LEFT]) + '/' + str(self.currentItem[RIGHT])

    def moveCursorUp(self):
        if self.currentPane == LEFT:
            self.rightPanes[self.currentItem[LEFT]].visible = False
            self.leftButtons[self.currentItem[LEFT]].active = False
            self.currentItem[self.currentPane] = self.model.prevLeftItem(self.currentItem[LEFT])
            self.leftButtons[self.currentItem[LEFT]].active = True
            self.rightPanes[self.currentItem[LEFT]].visible = True
        else:
            self.rightButtons[self.currentRightKey()].active = False
            self.currentItem[self.currentPane] = self.model.prevRightItem(self.currentItem[LEFT], self.currentItem[RIGHT])
            self.rightButtons[self.currentRightKey()].active = True
    def moveCursorDown(self):
        if self.currentPane == LEFT:
            self.rightPanes[self.currentItem[LEFT]].visible = False
            self.leftButtons[self.currentItem[LEFT]].active = False
            self.currentItem[self.currentPane] = self.model.nextLeftItem(self.currentItem[LEFT])
            self.leftButtons[self.currentItem[LEFT]].active = True
            self.rightPanes[self.currentItem[LEFT]].visible = True
        else:
            self.rightButtons[self.currentRightKey()].active = False
            self.currentItem[self.currentPane] = self.model.nextRightItem(self.currentItem[LEFT], self.currentItem[RIGHT])
            self.rightButtons[self.currentRightKey()].active = True

    def show(self, model):
        self.model = model
        self.menu = self.buildUI(self.ui.vp.size)
        self.currentPane = LEFT
        self.currentItem[LEFT] = model.defaultLeftItem()
        self.currentItem[RIGHT] = None
        self.leftButtons[self.currentItem[LEFT]].active = True
        self.rightPanes[self.currentItem[LEFT]].visible = True

    def buildUI(self, size):
        menuColor = (64, 64, 64, 128)
        panelColor = (16, 16, 16, 128)
        buttonColor = (192, 192, 96, 128)

        pos = size * 0.05
        size = size * 0.9

        menu = gui.Pane(menuColor, pos, size)
        lpPos = size * 0.02
        lpSize = size * (0.30, 0.96)
        leftPane = gui.Pane(panelColor, lpPos, lpSize)

        menu.addChild(leftPane)

        i = 0
        for key, item in self.model.leftItems():
            button = gui.Button(item, buttonColor, lpSize * (0.03, 0.02 + i * 0.07), lpSize * (0.94, 0.05))
            leftPane.addChild(button)
            if self.currentItem[LEFT] == i:
                button.active = True
            self.leftButtons[key] = button
            self.rightPanes[key] = self.createRightPane(size, key)
            menu.addChild(self.rightPanes[key])
            i += 1

        return menu

    def createRightPane(self, size, key):
        panelColor = (16, 16, 16, 128)
        buttonColor = (192, 192, 96, 128)

        rpPos = size * (0.34, 0.02)
        rpSize = size * (0.64, 0.96)
        rightPane = gui.GridPane(panelColor, rpPos, rpSize, 4)
        rightPane.visible = False

        i = 0
        for rkey, item in self.model.rightItems(key):
            button = gui.ShopWidget(item, buttonColor)
            self.rightButtons[str(key) + '/' + str(rkey)] = button
            rightPane.addChild(button)
            if self.currentItem[RIGHT] == i:
                button.active = True
            i += 1

        return rightPane

    def render(self, surface):
        if self.model is not None:
            self.menu.render(surface, np.zeros(2), np.array((surface.get_width(), surface.get_height())))

class MapMenu:
    def __init__(self, ui):
        self.ui = ui
        self.model = None

    def render(self, surface):
        if self.model is None:
            return

        size = np.array((surface.get_width(), surface.get_height()))

        pos = size * 0.025
        size = size * 0.95
        menuColor = (64, 64, 64, 192)

        outer = gui.Pane(menuColor, pos, size, pygame.BLEND_RGBA_ADD)

        pos = size * 0.02
        size = size * 0.96
        inner = gui.MapPane(menuColor, pos, size, pygame.BLEND_RGBA_MULT)
        outer.addChild(inner)

        for sector in sectors.all():
            inner.addChild(gui.SectorMarker(sector))
        inner.addChild(gui.ShipMarker(self.model.currentSector, self.model.objects.p[0], self.model.objects.dp[0]))

        outer.render(surface, np.zeros(2), size)


    def actionPerformed(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return 'game'
        return 'menu'
