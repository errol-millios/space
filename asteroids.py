import glob
import random
import pygame as pg

from mobiles import Mobile

class Asteroid(Mobile):
    def __init__(self, sprite):
        Mobile.__init__(self, sprite)

_files = glob.glob('resources/sprites/asteroids/*.png')
_N = len(_files)
_sprites = {}

def get():
    i = random.randint(0, _N - 1)
    filename = _files[i]
    if filename not in _sprites:
        _sprites[filename] = pg.image.load(filename)
    return Asteroid(_sprites[filename])
