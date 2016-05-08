import pygame as pg
import random
import yaml
import planetgen
import numpy as np

from dockable import Planet

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    print 'libyaml not installed?'
    from yaml import Loader, Dumper

class Sector:
    def __init__(self, name, pos, planets):
        self.name = name
        self.pos = np.array(pos)
        self.planets = planets

def emptySector(pos):
    return Sector(None, pos, [])

scale = None
_sectors = None
with open('resources/sectors.yaml', 'r') as file:
    data = yaml.load(file.read())
    scale, _sectors = data['scale'], data['sectors']

_positionIndex = {tuple(s[1]['pos']): s[1] for s in _sectors.iteritems()}

_loadedSectors = {}

def loadPlanetSprite(name, radius, seed):
    size = radius * 2
    fn = 'resources/sprites/planets/%s.%s.%s.png' % (name, size, seed)
    try:
        return pg.image.load(fn)
    except pg.error:
        planetgen.generate(name, size, fn, seed)
        return pg.image.load(fn)

def loadPlanets(data):
    return [(
        p['pos'],
        Planet(p['name'], p['r'], (192, 192, 192), loadPlanetSprite(p['sprite'], p['r'], None if 'seed' not in p else p['seed']))
         ) for p in data]

def loadSector(name, data):
    return Sector(name, data['pos'], loadPlanets(data['planets']))

def get(name):
    try:
        return loadSector(name, _sectors[name])
    except KeyError:
        raise
        return None

def getByPosition(pos):
    pos = tuple(pos)
    if pos in _positionIndex:
        return loadSector(_positionIndex[pos]['name'], _positionIndex[pos])
    return emptySector(pos)

def all():
    return map(lambda a: loadSector(a['name'], a), _sectors.values())
