import sys
import pygame as pg
from random import random
import numpy as np
import timeit

import cPickle as pickle

import hashlib

import yaml

from shipgenerator import generate as generateShip, renderShip
from shipgenerator import vec

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    print 'libyaml not installed?'
    from yaml import Loader, Dumper

arr = lambda a: np.array(a)

def randomPoints():
    p1 = np.array([100, 200], dtype=float)
    p4 = np.array([1024 - 100, 768 - 200], dtype=float)

    v = p4 - p1
    vperp = perp(v / np.linalg.norm(v))

    r = (random() - 0.5)
    r += 20 * np.sign(r)

    p2 = p1 + v * random() + 10 * vperp * r

    r = (random() - 0.5)
    r += 20 * np.sign(r)

    p3 = p1 + v * random() + 10 * vperp * r

    return np.array([p1, p2, p3, p4])


def segments(pts, c, t):
    prev = None
    for p in pts:
        if prev is not None:
            pg.draw.line(screen, c, prev, p, t)
        prev = p


def randomSpecs():
    return [
        random() * 90 + 10,
        random() * 90 + 10,
        random() * 90,
        random() * 90,
        random() * 90,
        random() * 90,
        random() * 90,
        random() * 90,
        random() * 90,
        random() * 90
    ] + list(np.random.random(25))


pg.init()
size = (300 * 6, 300 * 3)
screen = pg.display.set_mode(size)
screen_rect = screen.get_rect()

killed = {}

def show(ships):
    screen.fill((0, 0, 0))
    i = 0
    font = pg.font.Font(None, 16)
    for x in xrange(6):
        for y in xrange(3):
            center = np.array((150 + x * 300, 150 + y * 300))
            pts = generateShip(ships[i])
            pts = 200 * pts + center
            pg.draw.polygon(screen, pg.Color('tomato'), pts)
            # for p in pts:
            #     pg.draw.line(screen, np.array((0, 0, 128)), p, p + (0, 5), 5)
            pg.draw.line(screen, np.array((0, 0, 255)), center, center + (0, 10), 10)
            ts = font.render(shipName(ships[i]), 1, (255, 255, 255))
            screen.blit(ts, center)
            if i in killed:
                pg.draw.polygon(screen, pg.Color('cyan'), pts, 2)
            # segments(pts, pg.Color('tomato'), 1)
            i += 1
    pg.display.flip()



def take_sample(population, k = 18):
    return [int(random() * len(population)) for i in xrange(k)]

def generateMore(population, addRandom = True):
    sample = np.transpose(vec(take_sample(population, 10), take_sample(population, 10)))
    newPopulation = []
    for s1i, s2i in sample:
        s1 = population[s1i]
        s2 = population[s2i]
        new = []
        for i in xrange(len(s1)):
            if random() < 0.75:
                mutation =  (random() * 0.3 + 0.85)
            else:
                mutation = 1
            if random() < 0.5:
                new.append(s1[i] * mutation)
            else:
                new.append(s2[i] * mutation)
        newPopulation.append(new)

    if addRandom:
        for i in xrange(10):
            newPopulation.append(randomSpecs())

    return newPopulation

with open('english3000.txt', 'r') as file:
    words = [l.strip() for l in list(file)]

wlen = len(words)


def shipName(specs):
    sha1 = hashlib.sha1()
    specs = map(float, specs)
    sha1.update(str(specs))
    digest = int(sha1.digest().encode('hex'), 16)
    return '%s-%s-%s' % (words[digest % wlen], words[(digest / wlen) % wlen], words[(digest / wlen / wlen) % wlen])


def dump(population):
    surface = pg.Surface((300, 300))


    names = {}

    for s in population:
        s = map(float, s)
        sha1 = hashlib.sha1()
        sha1.update(str(s))
        digest = int(sha1.digest().encode('hex'), 16)

        name = '%s-%s-%s' % (words[digest % wlen], words[(digest / wlen) % wlen], words[(digest / wlen / wlen) % wlen])

        nameIndex = 0
        checkName = name
        while checkName in names:
            checkName = '%s-%d' % (name, nameIndex)
            nameIndex += 1
        name = checkName

        with open('ships/%s.yaml' % name, 'w') as file:
            file.write(yaml.dump(s, Dumper=Dumper))
        renderShip(140 * generateShip(s) + (150, 150), surface)
        pg.image.save(surface, 'ships/%s.png' % name)
        surface.fill((0, 0, 0))

maxPopulation = 10

try:
    with open('population.pkl', 'r') as file:
        population = pickle.load(file)
except IOError:
    print 'Error loading population. Initializing with random data.'
    population = [randomSpecs() for i in xrange(maxPopulation)]



clock = pg.time.Clock()
running = True

sample = take_sample(population)
show([population[s] for s in sample])

while running:
    clock.tick(10)
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        elif event.type == pg.MOUSEBUTTONDOWN:
            pos = arr(event.pos)
            pos = np.round(pos / 300)
            index = pos[0] * 3 + pos[1]
            del population[sample[index]]
            sample = take_sample(population)
            show([population[s] for s in sample])
            print 'population', len(population)
            with open('population.pkl', 'w') as file:
                pickle.dump(population, file)
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                running = False
            elif event.key == pg.K_g:
                dump(population)
            elif event.key == pg.K_r:
                sample = take_sample(population)
                show([population[s] for s in sample])
            elif event.key == pg.K_a:
                print 'generating more'
                population += generateMore(population)


    if len(population) < 18:
        print 'generating more'
        population += generateMore(population)
pg.quit()
sys.exit()
