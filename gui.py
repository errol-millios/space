import pygame
from pygame.locals import Rect
import numpy as np
import numpy.linalg as LA
import sectors

def renderText(font, text, color):
    return [font.render(t, 1, color) for t in text.split('\n') if t != '']

class Component(object):
    def __init__(self):
        self.visible = True
        self.children = []

    def render(self, surface, parentPos, parentSize):
        for child in self.children:
            if child.visible:
                child.render(surface, parentPos, parentSize)

    def addChild(self, child):
        self.children.append(child)

class Pane(Component):
    def __init__(self, color, pos, size, fillFlags = pygame.BLEND_RGBA_ADD):
        Component.__init__(self)
        self.color = color
        self.pos = pos
        self.size = size
        self.fillFlags = fillFlags if fillFlags is not None else 0

    def render(self, surface, parentPos, parentSize, renderChildren = True):
        pos = self.pos + parentPos
        size = self.size
        self._pos = pos
        self._size = size
        self._rect = Rect(pos, size)
        surface.fill(self.color, self._rect, self.fillFlags)

        if renderChildren:
            for child in self.children:
                if child.visible:# and child.pos is not None:
                    child.render(surface, pos, size)

class Button(Pane):
    def __init__(self, text, color, pos = None, size = (94, 5)):
        Pane.__init__(self, color, pos, size, None)
        font = pygame.font.Font(None, 28)
        self.active = False
        self.text = renderText(font, text, (64, 64, 64))
        self.textPos = lambda p, s: p * (1.01, 1.01)

    def render(self, surface, parentPos, parentSize):
        Pane.render(self, surface, parentPos, parentSize)

        pos = self.textPos(self._pos, self._size)
        for ts in self.text:
            surface.blit(ts, pos)
            pos += (0, ts.get_height() * 1.1)

        if self.active:
            pygame.draw.rect(surface, (64, 64, 128), self._rect, 3)

class ShopWidget(Button):
    def __init__(self, text, color, pos = None, size = (23, 23)):
        Button.__init__(self, text, color, pos, size)
        font = pygame.font.Font(None, 14)
        self.text = renderText(font, text, (64, 64, 64))
        # self.textPos = lambda p, s: p * 1.01 + s * (0, 0.8)

class GridPane(Pane):
    def __init__(self, color, pos, size, cols):
        Pane.__init__(self, color, pos, size)
        self.cols = cols
    def render(self, surface, parentPos, parentSize):
        Pane.render(self, surface, parentPos, parentSize, False)
        x = 0
        y = 0
        pos = np.zeros(2)
        childSize = 0.92 * self.size / float(self.cols)
        for child in self.children:
            if child.visible:
                if x >= self.cols:
                    y += 1
                    x = 0
                    pos = childSize * np.array((0, 1.05)) * y
                child.pos = self.pos + pos + 0.02 * self.size
                child.size = childSize
                child.render(surface, parentPos, parentSize)
                pos = pos + child.size * np.array((1.05, 0))
                x += 1
        pygame.draw.rect(surface, (64, 64, 128), self._rect, 3)

class MapPane(Pane):
    def __init__(self, color, pos, size, fillFlags = pygame.BLEND_RGBA_ADD):
        Pane.__init__(self, color, pos, size, fillFlags)

    def render(self, surface, parentPos, parentSize):
        Pane.render(self, surface, parentPos, parentSize)

class SectorMarker(Component):
    def __init__(self, sector):
        Component.__init__(self)
        self.sector = sector
        self.font = pygame.font.Font(None, 14)


    def render(self, surface, parentPos, parentSize):
        markerSize = 2 * sectors.scale / 1000
        pos = (parentSize / 2) + ((self.sector.pos) * sectors.scale * 2 / 1000)

        size = np.array((markerSize, markerSize))
        rect = Rect(pos - (markerSize / 2), size)
        pygame.draw.rect(surface, (64, 64, 64, 16), rect)

        name = self.font.render(self.sector.name, 1, (255, 255, 255))
        surface.blit(name, pos - (name.get_width() / 2, -name.get_height()))

class ShipMarker(Component):
    def __init__(self, sector, pos, vel):
        Component.__init__(self)
        self.sector = sector
        self.pos = pos
        self.vel = vel
        self.which = 0

    def render(self, surface, parentPos, parentSize):
        sectorPos = (parentSize / 2) + ((self.sector.pos) * sectors.scale * 2 / 1000)
        pos = sectorPos + (10 * self.pos / (sectors.scale))
        color = (255, 255, 255) if self.which == 1 else (255, 255, 128)
        self.which = 1 - self.which
        speed = LA.norm(self.vel)
        if speed > 0.01:
            velEnd = 1 + pos + 10 * self.vel / speed
            pygame.draw.line(surface, color, pos + (0, 1), velEnd)
        pygame.draw.line(surface, color, pos, pos + (0, 3), 3)
