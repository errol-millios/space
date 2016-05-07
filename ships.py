import pygame
import weapons
import random
from mobile import Mobile
import yaml

import shipgenerator

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    print 'libyaml not installed?'
    from yaml import Loader, Dumper

generatedSprites = {}

def loadGeneratedSprite(name, color, size, rotation):
    key = '%s-%s-%s-%s' % (name, color, size, rotation)

    if key not in generatedSprites:
        print 'loading sprite ' + key
        with open('ships-keep/%s.yaml' % name, 'r') as file:
            specs = yaml.load(file.read())
            points = 300 * shipgenerator.generate(specs)
            surface = pygame.Surface((500, 500)).convert_alpha()
            surface.fill((0, 0, 0, 0))
            pygame.draw.polygon(surface, color, points + (250, 250))
            generatedSprites[key] = pygame.transform.rotate(pygame.transform.smoothscale(surface, (size, size)), rotation).convert_alpha()

    return generatedSprites[key]

def shipSprite(spriteDef, color):
    if color is None:
        color = (128, 128, 128)
    name, size, rotation = spriteDef
    if name == '_rect':
        sprite = pygame.Surface((size, rotation)).convert_alpha()
        sprite.fill(color)
        return sprite

    return loadGeneratedSprite(name, color, size, rotation)


class Ship(Mobile):
    def __init__(self, name, data):
        Mobile.__init__(self)
        self.name = name
        self.weapons = []
        self.inventory = {}
        self.lastFired = None
        multipliers = frozenset(['turnRate', 'thrust'])
        sprite = None
        color = None
        for key, value in data.iteritems():
            if key == 'sprite':
                sprite = value
            elif key == 'color':
                color = value
            elif key in multipliers:
                setattr(self, key, getattr(self, key) * value)
            elif key == 'weapons':
                self.weapons = [weapons.get(w) for w in value]
            else:
                setattr(self, key, value)

        if sprite is not None:
            self.sprite = shipSprite(sprite, color)

    def serialize(self):
        return self.name

_ships = None
with open('resources/ships.yaml', 'r') as file:
    _ships = yaml.load(file.read())

def get(name):
    try:
        return Ship(name, _ships[name])
    except KeyError:
        return None

def getRandom():
    names = _ships.keys()
    name = names[int(random.random() * len(names))]
    return Ship(name, _ships[name])

def getNext(name):
    if name == 'shuttle':
        return 'freighter'
    if name == 'freighter':
        return 'fighter'
    if name == 'fighter':
        return 'bomber'
    if name == 'bomber':
        return 'escape-pod'
    if name == 'escape-pod':
        return 'shuttle'

"""
Lacrimosa dies illa,
Qua resurget ex favilla,
Judicandus homo reus.
Huic ergo parce, Deus:
Pie Jesu Domine,
Dona eis requiem. Amen.
"""
