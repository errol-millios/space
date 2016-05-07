import pygame as pg

class Dockable:
    def __init__(self, sprite):
        self.sprite = sprite
        self.name = None

class Planet(Dockable):
    def __init__(self, name, radius, color, sprite):
        # name, radius, color
        # sprite = pg.image.load('/home/tarn/code/py/space/planet/high-quality/small-20150606_140018.png')
        # sprite = pg.Surface((int(radius * 2.1), int(radius * 2.1))).convert_alpha()
        # sprite.fill((0, 0, 0, 0))
        # pg.draw.circle(sprite, color, (int(radius * 1.05), int(radius * 1.05)), int(radius))
        Dockable.__init__(self, sprite)
        self.name = name
        self.radius = radius
        self.color = color
    def __repr__(self):
        return str(self.name)

    def serialize(self):
        return self.name
