import pygame
import copy
import yaml
import mobiles
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
        return mobiles.Mobile(self.sprite)


_weapons = None
with open('resources/weapons.yaml', 'r') as file:
    _weapons = yaml.load(file.read())

def generateWeaponSprite(size, color):
    sprite = pygame.Surface(size).convert_alpha()
    sprite.fill(color)
    return sprite

catalog = inventory.Catalog()
def get(name):
    parameters = [
        catalog.get(name, 'name'),
        catalog.get(name, 'desc'),
        _weapons[name]['type'],
        generateWeaponSprite(*_weapons[name]['sprite']) if 'sprite' in _weapons[name] else None,
        _weapons[name]['color'] if 'color' in _weapons[name] else None,
        _weapons[name]['interval'] if 'interval' in _weapons[name] else None,
        _weapons[name]['lifetime'] if 'lifetime' in _weapons[name] else None,
        _weapons[name]['spread'],
        _weapons[name]['energy']
    ]
    return Weapon(*parameters)
