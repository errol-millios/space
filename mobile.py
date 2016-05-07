import pygame
import numpy as np
import math
import random
from util import signum


_defaultSprite = None

def defaultSprite():
    global _defaultSprite
    if _defaultSprite is None:
        _defaultSprite = pygame.Surface((20, 20)).convert_alpha()
        _defaultSprite.fill((255, 0, 0, 128))
    return _defaultSprite

class Mobile:
    def __init__(self, sprite = None):
        self.sprite = sprite if sprite is not None else defaultSprite()
        self.lifetime = None
        self.thrust = 10000
        self.turnRate = 100
        self.mass = 1
        self.hitRadius = 0
        self.incomingCollision = None
        self.parent = None
        self.shieldCapacity = 200
        self.shieldCharge = 200
        self.hullCapacity = 100
        self.hullIntegrity = 100

        self.energy = 100
        self.energyCapacity = 100
        self.energyProductionRate = 5
        self.shieldEfficiency = 0.8
        self.shieldLoss = 0.1
        self.maxShieldEnergyUsageRate = 1.1
        self.target = None
        self.targeted = False

    def step(self):
        if self.lifetime is not None:
            self.lifetime -= 1
        self.energy += self.energyProductionRate
        self.shieldCharge -= self.shieldLoss
        energyRequired = (self.shieldCapacity - self.shieldCharge) / self.shieldEfficiency
        energyRequired = min(energyRequired, self.maxShieldEnergyUsageRate * self.energyProductionRate)
        if self.energy > energyRequired:
            self.energy -= energyRequired
            self.shieldCharge += energyRequired * self.shieldEfficiency
        else:
            self.shieldCharge += self.energy * self.shieldEfficiency
            energyRequired -= self.energy
            self.energy = 0
        self.energy = min(self.energy, self.energyCapacity)

    def serialize(self):
        return None

class Debris(Mobile):
    def __init__(self):
        sprite = pygame.Surface((10, 10)).convert_alpha()
        sprite.fill((0, 0, 0, 0))
        points = 5 * (1 + np.random.random((int(round(3 + random.random() * 5)), 2)))
        pygame.draw.polygon(sprite, (128, 128, 128), points)
        Mobile.__init__(self, sprite)
        self.lifetime = 1000
        self.shieldCapacity = 0
        self.shieldCharge = 0
        self.hullCapacity = 0
        self.hullIntegrity = 0
        self.energy = 0
        self.energyCapacity = 0
        self.energyProductionRate = 0
