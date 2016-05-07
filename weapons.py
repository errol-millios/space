import pygame
import copy

from mobile import Mobile

import inventory

class Weapon:
    def __init__(self, name, description, type, sprite, color, interval, lifetime, spread, energy):
        self.name = name
        self.description = description
        self.type = type
        self.sprite = sprite
        self.color = color

        self.lifetime = lifetime
        self.spread = spread
        self.interval = interval
        self.energyPerShot = energy
        self.efficiency = 0

        self.lastFired = None
        self.firing = False

    def projectile(self):
        return Mobile(self.sprite)

instances = None

def make():
    instances = {}

    catalog = inventory.Catalog()

    instances['laser'] = Weapon(catalog.get('laser', 'name'), catalog.get('laser', 'desc'), 'beam', None, (255, 0, 0, 192), None, 1000, 5, 4)

    instances['tractor'] = Weapon(catalog.get('tractor', 'name'), catalog.get('tractor', 'desc'), 'target-beam', None, (0, 255, 0, 192), None, 1000, 5, 4)

    sprite = pygame.Surface((10, 2)).convert_alpha()
    sprite.fill((0, 128, 255, 192))
    instances['plasma'] = Weapon(catalog.get('plasma', 'name'), catalog.get('plasma', 'desc'), 'projectile', sprite, None, 3, 20, 10, 20)

    sprite = pygame.Surface((2, 2)).convert_alpha()
    sprite.fill((192, 192, 192, 255))
    instances['railgun'] = Weapon(catalog.get('railgun', 'name'), catalog.get('railgun', 'desc'), 'projectile', sprite, None, 3, 1000, 7, 10)
    return instances

def get(name):
    global instances
    if instances is None:
        instances = make()
    return copy.copy(instances[name])
