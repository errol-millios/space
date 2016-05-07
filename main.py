#!/usr/bin/env python2
import numpy as np
import numpy.linalg as LA
import scipy.misc as misc
import math

from random import random, randint
import copy

import os
import sys

import pygame as pg
from pygame.locals import *
from pygame.compat import geterror

import cPickle as pickle

if not pg.font: print ('Warning, fonts disabled')
if not pg.mixer: print ('Warning, sound disabled')


import weapons
import ships
from mobile import Mobile, Debris
import inventory
import menu
import ai
from dockable import Planet
from physics import PhysicalObjects, FixedPhysicalObjects
import sectors

from shipgenerator import vec

"""

>>> import numpy as np
>>> np.array([1,2,3])
array([1, 2, 3])
>>> a=np.array([1,2,3])
>>> np.transpose(a)
array([1, 2, 3])
>>> a=np.array([[1,2,3]])
>>> np.transpose(a)
array([[1],
       [2],
       [3]])
>>> np.transpose(a) - a
array([[ 0, -1, -2],
       [ 1,  0, -1],
       [ 2,  1,  0]])
>>> a - np.transpose(a)
array([[ 0,  1,  2],
       [-1,  0,  1],
       [-2, -1,  0]])
>>> b = np.array([[0.1, 0.2, 0.3]])
>>> a - b
array([[ 0.9,  1.8,  2.7]])
>>> b - a
array([[-0.9, -1.8, -2.7]])
>>> c = np.transpose(a)
>>> b - c
array([[-0.9, -0.8, -0.7],
       [-1.9, -1.8, -1.7],
       [-2.9, -2.8, -2.7]])
>>> c - b
array([[ 0.9,  0.8,  0.7],
       [ 1.9,  1.8,  1.7],
       [ 2.9,  2.8,  2.7]])
>>>


"""













"""
+ OK Physical properties in numpy arrays for efficient updates
+ OK ViewPort anchored to specific object
+ Save game state
+ Projectile collisions (naive)
+ Beam weapons
+ Physical projectile weapons
+ Energy projectile weapons (plasma; reduced shield effectiveness)
- Ship upgrades
- Upgrades have space, mass
- Ship acceleration, rotation affected by mass
- Ship supplies (mostly replicated but emergency supply required for e.g. escape pods)

- minimap


- Runge Kutta?

- Render only objects in view port
- Calculate gravitational forces for objects in current and adjacent sectors only
- Divide all space into sectors
- Max velocity enforced with increased effective mass
- Generate star systems along a treeish graph
- Land on planets (when moving slow enough)
- Disable gravitational forces for player controlled object
- Shields are EM or gravitational repulsors
- Generate planet image with spherical landscape rendered into circle
- Cargo pods (+space +mass)
- Ship energy (weapons, shield, propulsion)
- Hyperspace (outside of normal space, travel x units in hyperspace corresponds to travel ax units on normal space, a >1)
- Hyperspace drives energy intensive
- Jump gates that tunnel ships through hyperspace at reduced energy cost (passive; use ships' own energy)
- Sector size should be big enough that normal propulsion can't cross in any reasonable time
- Space stations buildable: solar collectors, weapons platforms
- Mining uninhabited planets
- Planetary defense satellites
- Trading resources mined or produced
- Producable resources
- Planet classes
- Ship classes: start with tiny shuttle, no hyperspace, not enough energy for jumpgates
- Missions: ferry passengers, transport cargo, kill bad guys
- Reputation
- Bad guy hangouts
- Statistical simulation of groups out of interaction range (ship locations change, resources collected, things destroyed?)
- Story component. Player provides narrative? Narrative assist?
- Random breakage (MTBF)
- Skills (trading, mining, repair, weapons systems, navigation, ...)
- Zoom

"""

from util import trunc, signum

verbose = 1

def mkEvent(type, arguments = []):
    return (type, arguments)


class StatusBar:
    def __init__(self):
        self.topText = 'All systems nominal.'
        self.bottomText = 'Cool.'
        self.messageTime = 0
        self.font = pg.font.Font(None, 16)

    def notify(self, message, duration = 30):
        self.bottomText = message
        self.messageTime = 30

    def step(self, tick):
        self.messageTime -= 1
        if self.messageTime < 0:
            self.bottomText = None

    def render(self, surface):
        if self.topText is not None:
            text = self.font.render(self.topText, 1, (255, 255, 255))
            surface.blit(text, (0, 0))

        if self.bottomText is not None:
            text = self.font.render(self.bottomText, 1, (255, 255, 255))
            surface.blit(text, (0, surface.get_height() - text.get_height()))

class UI:
    def __init__(self, size, offset):
        self.vp = ViewPort(size, offset)
        self.statusBar = StatusBar()
        self.game = None
        self.playerShip = None

        self.menu = None
        self.mode = 'game'
        self.quit = False
        self.turning = 0
        self.acceleration = 0
        self.lastKey = None

        self.isDecelerating = False
        self.isFiring = False

        self.playerWeapons = [
            [weapons.get('railgun')],
            [weapons.get('plasma')],
            [weapons.get('laser')],
            [weapons.get('tractor')]
        ]

        self.weaponIndex = 0

    def step(self, frame, tick):
        self.playerShip.turn(self.turning)
        self.playerShip.accel(self.acceleration)
        if self.isDecelerating:
            self.playerShip.decel()
        if self.isFiring:
            self.playerShip.fire(frame)

        # self.vp.step();
        self.statusBar.step(tick)
        self.vp.focus(self.game.objects.p[0])

    def handleInputEvent(self, event):
        if self.mode == 'menu':
            self.mode = self.menu.actionPerformed(event)
            return None

        if event.type == KEYDOWN:
            if event.key == pg.K_ESCAPE:
                self.quit = True

            elif event.key == pg.K_BACKSPACE:
                self.playerShip.nextShip()

            elif event.key == pg.K_UP:
                self.acceleration = 1
                self.isDecelerating = False

            elif event.key == pg.K_DOWN:
                self.acceleration = -1
                self.isDecelerating = False

            elif event.key == pg.K_z:
                self.acceleration = 0
                self.isDecelerating = True

            elif event.key == pg.K_LEFT:
                self.turning = 1
                self.isDecelerating = False

            elif event.key == pg.K_RIGHT:
                self.turning = -1
                self.isDecelerating = False

            elif event.key == pg.K_h:
                self.playerShip.warpHome()

            elif event.key == pg.K_SPACE:
                self.isFiring = True

            elif event.key == pg.K_d or event.key == pg.K_l:
                self.setMenu(self.game.dock(0))

            elif event.key == pg.K_LEFTBRACKET:
                N = len(self.playerWeapons)
                self.weaponIndex = (N + self.weaponIndex - 1) % N
                self.game.objects.gamestate[0].weapons = self.playerWeapons[self.weaponIndex]

            elif event.key == pg.K_RIGHTBRACKET:
                self.weaponIndex = (self.weaponIndex + 1) % len(self.playerWeapons)
                self.game.objects.gamestate[0].weapons = self.playerWeapons[self.weaponIndex]

            elif event.key == pg.K_g:
                self.game.toggleGravity()

            elif event.key == pg.K_f:
                self.game.toggleFriction()
            elif event.key == pg.K_s:
                self.game.spawnRandomShips()
            elif event.key == pg.K_n:
                self.game.spawnNearbyShip()
            elif event.key == pg.K_w:
                if self.game.currentSector == 'zerozeroone':
                    self.game.currentSector = 'pelagos'
                else:
                    self.game.currentSector = 'zerozeroone'
                self.game.loadSector(self.game.currentSector)
            elif event.key == pg.K_m:
                self.setMenu(self.game.mapMenu(0))

            elif event.key == pg.K_t:
                self.playerShip.nearestTarget()

            self.lastKey = event.key


        elif event.type == KEYUP:
            if event.key == pg.K_UP:
                self.acceleration = 0
                self.isDecelerating = False

            elif event.key == pg.K_DOWN:
                self.acceleration = 0
                self.isDecelerating = False

            elif event.key == pg.K_LEFT:
                if self.lastKey != pg.K_RIGHT:
                    self.turning = 0

            elif event.key == pg.K_RIGHT:
                if self.lastKey != pg.K_LEFT:
                    self.turning = 0

            elif event.key == pg.K_SPACE:
                self.isFiring = False

            elif event.key == pg.K_z:
                self.acceleration = 0
                self.isDecelerating = False

            self.lastKey = event.key

        return None

    def setMenu(self, strategy):
        if strategy is not None:
            menuConstructor, model = strategy
            self.menu = menuConstructor(self)
            self.menu.model = model
            self.mode = 'menu'


class ViewPort:
    def __init__(self, size, offset):
        self.pos = np.zeros(2)
        self.size = size
        self.offset = offset

    def focus(self, pos):
        self.pos = pos - self.offset

class Starfield:
    # TODO render to surface and then blit
    def __init__(self):
        gray = np.array((192, 192, 192))
        self.layers = [
            (0, 0.25, 0.1 * gray),
            (1, 0.1, 0.25 * gray),
            (2, 0.05, 0.5 * gray),
            (3, 0.01, 1.25 * gray)]
        self.size = np.array((1024, 768)) * 1.25
        self.center = self.size / 2
        self.stars = np.random.random((len(self.layers), 25, 2)) * self.size - self.center

    def render(self, viewLocation, surface):
        for i, depth, color in self.layers:
            for p in np.remainder(self.stars[i] - depth * viewLocation, self.size):
                pg.draw.line(surface, color, p, p + (2, 0), 2)

class DockingMenuModel:
    def __init__(self, game):
        self.game = game

        partsList = [part['name'] for part in inventory.Catalog().items().values()]

        self.items = [
            ('Employment', ['Ferry Passengers', 'Deliver Cargo', 'Make Irrefusable Offer']),
            ('Parts', partsList),
            ('Shipyard', ['Kestrel', 'Zephyr', 'Passenger Shuttle']),
            ('Space Diner', ['Soup', 'Hamburger', 'Special'])
        ]


    def leftItems(self):
        return enumerate([i[0] for i in self.items])

    def rightItems(self, leftSelection):
        return enumerate(self.items[leftSelection][1])

    def defaultLeftItem(self):
        return 0

    def defaultRightItem(self):
        return 0

    def nextLeftItem(self, i):
        return (i + 1) % len(self.items)

    def prevLeftItem(self, i):
        N = len(self.items)
        return (N + i - 1) % N

    def nextRightItem(self, i, j):
        return (j + 1) % len(self.items[i][1])

    def prevRightItem(self, i, j):
        N = len(self.items[i][1])
        return (N + j - 1) % N

class Game:
    def __init__(self, ui, screen):
        self.screen = screen
        self.minimap = None
        self.infoPanelInfo = None
        self.minimapPos = None
        self.initGraphics()

        self.ui = ui

        self.puters = []

        self.enableGravity = False
        self.enableFriction = False
        self.enableSpeedLimit = False
        self.objects = PhysicalObjects(1, Mobile)
        self.objects.theta = (np.random.random(self.objects.cardinality) - 0.5) * 360

        self.objects.p[0] = (-10000, -10000) # (np.random.random(2) - 0.5) * 200
        self.objects.dp[0] = (0, 0)
        self.objects.gamestate[0] = ships.get('fighter')

        for m in self.objects.gamestate:
            m.sprite = m.sprite.convert_alpha()

        self.fixedObjects = FixedPhysicalObjects(0, lambda: None)

        self.loadSector(sectors.get('zerozeroone'))

        # for i in xrange(self.fixedObjects.cardinality):
        #     self.fixedObjects.p[i] = (20 * 1024 * (random() - 0.5), 20 * 768 * (random() - 0.5))
        #     self.fixedObjects.mass[i] = 100 * random() * 100


        # d = 96
        # l = 192
        # self.fixedObjects.gamestate = [Planet('Lucky Strike', 80 * random() + 40, (d, d, l)),
        #                                Planet("God's Acre", 80 * random() + 40, (d, l, d)),
        #                                Planet('We Made It', 80 * random() + 40, (d, l, l)),
        #                                Planet('Last Chance', 80 * random() + 40, (l, d, d)),
        #                                Planet('New Hope', 80 * random() + 40, (l, d, l))]

        self.starfield = Starfield()

        ui.game = self
        ui.playerShip = self.getMobileController(0)

    def loadSector(self, sector):
        if sector.name is None:
            self.ui.statusBar.notify('Entering sector ' + '-'.join(map(str, sector.pos)) + '.')
        else:
            self.ui.statusBar.notify('Entering ' + sector.name + '.')
        self.currentSector = sector
        # sector.pos do something with it

        planets = sector.planets

        self.fixedObjects = FixedPhysicalObjects(len(planets), lambda: None)

        for i, info in enumerate(planets):
            self.fixedObjects.p[i], self.fixedObjects.gamestate[i] = info

    def toggleGravity(self):
        self.enableGravity = not self.enableGravity
    def toggleFriction(self):
        self.enableFriction = not self.enableFriction

    def step(self, tick, ticking):
        if ticking and tick % 3:
            self.puters = [p for p in self.puters if p.step()]

        dt = 0.1

        # x = x0 + v0 t + .5 a t^2
        # v = v0 + a t
        # a = a

        if self.enableGravity:
            dp = self.objects.p[:,None] - self.fixedObjects.p
            distanceFactor = 0.1 / (1 + np.sqrt(np.sum(dp * dp, axis=2)))
            self.objects.dp += 100 * -np.sum(dp * distanceFactor[:,:,None], axis=1) * 0.1
            if verbose > 1:
                print('p', tuple(self.objects.p[0]), 'ddp', tuple(self.objects.ddp[0]), 'dp', tuple(dp[0]), 'dF', tuple(distanceFactor[0]))
        self.objects.p += self.objects.dp * dt
        self.objects.dp += self.objects.ddp * dt
        self.objects.theta += self.objects.dtheta * dt
        self.objects.dtheta += self.objects.ddtheta * dt

        if self.enableFriction:
            self.objects.dp *= 0.9

        if self.enableSpeedLimit:
            for i in xrange(self.objects.cardinality):
                if not self.objects.canCollide[i]:
                    magnitude = LA.norm(self.objects.dp[i])
                    if magnitude > 400:
                        self.objects.dp[i] *= 400 / magnitude

        test = np.abs(self.objects.dtheta) > 50
        sgn = np.sign(self.objects.dtheta)
        self.objects.dtheta = 50 * test * sgn + (1 - test) * self.objects.dtheta

        self.naiveCollisionDetection()

        # if random() < 0.1 and self.objects.cardinality < 100:
        #     self.spawnRandomShips()

        x, y = self.objects.p[0]
        smax = sectors.scale
        smin = -sectors.scale
        ox = 0
        oy = 0
        if x > smax:
            ox = 1
        elif x < smin:
            ox = -1
        if y > smax:
            oy = 1
        elif y < smin:
            oy = -1

        offset = np.array((ox, oy))
        self.loadSector(sectors.getByPosition(self.currentSector.pos + offset))
        self.objects.p[0] -= offset * sectors.scale * 2

        if verbose > 2:
            KE = 0.5 * np.sum(np.prod(self.objects.dp, axis=0))
            print('KE', KE)

    def spawnNearbyShip(self):
        index = self.objects.add(1, lambda: ships.getRandom())

        r = (np.random.random(2) - 0.5)
        r *= 100 / LA.norm(r)

        self.objects.p[index] = self.objects.p[0] + r

        # self.puters.append(ai.FollowTarget(self.getMobileController(index), self.objects.ref(0))) # randint(0, self.objects.cardinality - 1))))


    def spawnRandomShips(self):
        if self.fixedObjects.cardinality < 1:
            return

        target = randint(0, self.fixedObjects.cardinality - 1)
        targetp = self.fixedObjects.p[target]

        n = int(5 * random()**2) + 1

        first = self.objects.add(n, lambda: ships.getRandom())
        last = first + n

        center = np.random.random(2) - 0.5
        center *= 10000 / LA.norm(center)

        trajectory = targetp - center
        trajectory /= LA.norm(trajectory)

        self.objects.p[first:last] = center + (np.random.random((n, 2)) - 0.5) * 100
        self.objects.theta[first:last] = 180 * math.atan2(-trajectory[1], trajectory[0]) / math.pi
        self.objects.dp[first:last] = trajectory * 200

        for i in xrange(first, last):
            self.puters.append(ai.StopAtDestination(self.getMobileController(i), targetp))

    def naiveCollisionDetection(self):
        projectileCondition = np.logical_and(self.objects.active, self.objects.canCollide)
        projectiles = np.compress(projectileCondition, self.objects.p, axis=0)
        projectileIndexMap = None
        if projectiles.shape[0] < 1:
            return
        dp = projectiles[:,None] - self.objects.p
        dp *= dp
        d2 = np.sum(dp, axis=2)

        maxHitRadius = 40 * 40

        for projectileIndex, targetIndex in np.transpose((d2 < maxHitRadius).nonzero()):
            if not self.objects.canCollide[targetIndex]:
                r2 = self.objects.gamestate[targetIndex].hitRadius
                r2 *= r2
                if d2[projectileIndex, targetIndex] > r2:
                    continue
                if projectileIndexMap is None:
                    projectileIndexMap = np.compress(projectileCondition, np.arange(self.objects.p.shape[0]), axis=0)
                if self.objects.gamestate[projectileIndexMap[projectileIndex]].parent == targetIndex:
                    continue
                if verbose > 2:
                    print 'naive collision of projectile %d (%d) with target %d' % (projectileIndex, projectileIndexMap[projectileIndex], targetIndex)
                self.objects.gamestate[targetIndex].incomingCollision = projectileIndexMap[projectileIndex]

    def renderMinimap(self, vp):
        minimapSize = 200

        w, h = 200, 200
        if self.minimap is None:
            minimap = pg.Surface([w, h])
        else:
            minimap = self.minimap
            minimap.fill((0, 0, 0))

        scale = 200.0 / (10 * 1024.0)
        offset = minimapSize / 2

        center = vp.pos + (512, 384)

        topLeft = center - (10 * 1024, 10 * 768)
        bottomRight = center + (10 * 1024, 10 * 768)

        indices = np.transpose(np.nonzero(np.logical_and(self.objects.p > topLeft, self.objects.p < bottomRight)))
        for i, j in indices:
            if not self.objects.active[i]:
                continue
            pos = scale * (self.objects.p[i] - center) + offset

            if self.objects.canCollide[i]:
                weight = 1
                color = (80, 80, 80)
            elif self.objects.gamestate[i].hitRadius < 1:
                weight = 1
                color = (40, 40, 40)
            else:
                weight = 2
                color = (255, 255, 255)
            pg.draw.line(minimap, color, pos, pos + (0, weight), weight)


        for i in xrange(self.fixedObjects.cardinality):
            pos = scale * (self.fixedObjects.p[i] - center) + offset
            if np.any(pos < (0, 0)) or np.any(pos > (w, h)):
                pos[0] = pos[0] if pos[0] >= 0 else 0
                pos[0] = pos[0] if pos[0] <= w else w
                pos[1] = pos[1] if pos[1] >= 0 else 0
                pos[1] = pos[1] if pos[1] <= h else h
                gs = self.fixedObjects.gamestate[i]
                pg.draw.circle(minimap, gs.color, map(int, pos), 5, 1)
            else:
                gs = self.fixedObjects.gamestate[i]
                pg.draw.circle(minimap, gs.color, map(int, pos), 5, 1)


        pg.draw.rect(minimap, (0, 128, 0), Rect(0, 0, w, h), 1)
        return (0, 0), minimap

    def renderInfoPanel(self, vp):
        size = vec(200, vp.size[1] - 200)
        if self.infoPanelInfo is None:
            panel = pg.Surface(size)
        else:
            panel = self.infoPanelInfo
            panel.fill((0, 0, 0))

        if self.fixedObjects.cardinality < 1:
            text = [(0, None, 'No planets detected in this system.')]
        else:
            text = [(0, None, '%d planet%s detected in this system:' % (self.fixedObjects.cardinality, 's' if self.fixedObjects.cardinality != 1 else ''))]

            for i in xrange(self.fixedObjects.cardinality):
                gs = self.fixedObjects.gamestate[i]
                text.append((1, gs.color, gs.name))

        text.append((0, None, '%d other %s.' % (self.objects.cardinality, 'bodies' if self.objects.cardinality != 1 else 'body')))

        font = pg.font.Font(None, 14)
        pos = np.zeros(2) + (2, 2)
        for indent, color, t in text:
            if color is None:
                color = (192, 192, 192)
            if t is None:
                t = '???'
            ts = font.render(t, 1, color)
            panel.blit(ts, pos + indent * np.array((12, 0)))
            pos += (0, ts.get_height() * 1.1)

        pg.draw.rect(panel, (0, 128, 0), Rect((0, 0), size), 1)
        return panel


    def initGraphics(self):
        self.background = pg.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.background.fill((0, 0, 0, 255))
        self.infoPanel = pg.Surface((200, self.screen.get_height()))
        self.mainPanel = pg.Surface((self.screen.get_width() - 200, self.screen.get_height()))
        self.minimapSurface = None
        self.minimapPos = None

    def renderFixedObjects(self, surface):
        for i in xrange(self.fixedObjects.cardinality):
            sprite = self.fixedObjects.gamestate[i].sprite
            swidth, sheight = sprite.get_size()
            # print(self.fixedObjects.p[i][0] - swidth / 2 - vp.x, self.fixedObjects.p[i][1] - sheight / 2 - vp.y)
            surface.blit(sprite, (self.fixedObjects.p[i][0] - swidth / 2, self.fixedObjects.p[i][1] - sheight / 2) - self.ui.vp.pos)

    def renderObjects(self, surface):
        for i, m in enumerate(self.objects.gamestate):
            if not self.objects.active[i]:
                continue
            m.step()
            if m.lifetime is not None and m.lifetime <= 0:
                self.objects.active[i] = False
                continue
            if m.incomingCollision is not None:
                if m.incomingCollision >= self.objects.cardinality:
                    pass # oops
                else:
                    self.weaponHit(self.objects.gamestate[m.incomingCollision].sourceWeapon, m, i)
                    self.objects.active[m.incomingCollision] = False
                    m.incomingCollision = None
            if m.sprite is not None:
                sprite = pg.transform.rotate(m.sprite, self.objects.theta[i])
                swidth, sheight = sprite.get_size()
                x, y = (self.objects.p[i][0] - swidth / 2, self.objects.p[i][1] - sheight / 2) - self.ui.vp.pos
                if x > 0 and y > 0 and np.any((x, y) < self.ui.vp.size):
                    cx, cy = x + swidth / 2, y + sheight / 2
                    try:
                        for weapon in m.weapons:
                            if weapon.firing:
                                if weapon.type == 'beam':
                                    weapon.firing = False
                                    start = np.array((cx, cy))
                                    direction = 2000 * np.array((math.cos(-math.pi * self.objects.theta[i] / 180), -math.sin(math.pi * self.objects.theta[i] / 180)))
                                    end = start + direction
                                    pg.draw.line(surface, weapon.color, start, end, 5)
                                elif weapon.type == 'target-beam' and m.target is not None:
                                    weapon.firing = False
                                    start = np.array((cx, cy))
                                    end = (self.objects.p[m.target.index] + (np.random.random(2) - 0.5) * 5) - self.ui.vp.pos
                                    pg.draw.line(surface, weapon.color, start, end, 5)
                    except AttributeError:
                        pass

                    surface.blit(sprite, (x, y))

                    if m.targeted:
                        p = np.array((cx, cy))
                        size = np.array((m.hitRadius, m.hitRadius))
                        p -= size / 2
                        pg.draw.lines(surface, (0, 255, 0), False, [p + (0, 10), p, p + (10, 0)])
                        p2 = p + size * (0, 1)
                        pg.draw.lines(surface, (0, 255, 0), False, [p2 - (0, 10), p2, p2 + (10, 0)])
                        p3 = p + size * (1, 0)
                        pg.draw.lines(surface, (0, 255, 0), False, [p3 + (0, 10), p3, p3 - (10, 0)])
                        p4 = p + size
                        pg.draw.lines(surface, (0, 255, 0), False, [p4 - (0, 10), p4, p4 - (10, 0)])

                    # pg.draw.line(surface, (255, 255, 255), (cx, cy), (cx + self.objects.ddp[i][0], cy + self.objects.ddp[i][1]))
                    if not self.objects.canCollide[i]:
                        if m.shieldCharge < m.shieldCapacity and m.shieldCharge > 0:
                            cp = np.array([cx, cy])
                            length = 30 * (float(m.shieldCharge) / m.shieldCapacity)
                            pg.draw.line(surface, (128, 128, 255), cp - (15, -10), cp - (15 - length, -10), 3)
                        if (m.hullIntegrity < m.hullCapacity or m.shieldCharge < m.shieldCapacity) and m.hullIntegrity > 0:
                            cp = np.array([cx, cy])
                            length = 30 * (float(m.hullIntegrity) / m.hullCapacity)
                            pg.draw.line(surface, (128, 255, 128), cp - (15, -14), cp - (15 - length, -14), 3)
                        if m.energy < m.energyCapacity and m.energy > 0:
                            cp = np.array([cx, cy])
                            length = 30 * (float(m.energy) / m.energyCapacity)
                            pg.draw.line(surface, (255, 255, 128), cp - (15, -18), cp - (15 - length, -18), 3)

        for i, m in enumerate(self.objects.gamestate):
            try:
                if m.annotation is None:
                    continue
                text = m.annotation
                x = self.objects.p[i][0] - swidth / 2 - vp.x
                y = self.objects.p[i][1] - sheight / 2 - vp.y
                cx = x + swidth / 2
                cy = y + sheight / 2
                font = pg.font.Font(None, 16)
                ts = font.render(text, 1, (255, 0, 0, 255))
                surface.blit(ts, (cx, cy))
            except AttributeError:
                pass

        self.ui.statusBar.topText = '({x:04.4f}, {y:04.4f}) ({xv:04.4f}, {yv:04.4f})[{speed:04.4f}] ({xa:04.4f}, {ya:04.4f})'.format(
            x=self.objects.p[0][0],
            y=self.objects.p[0][1],
            xv=self.objects.dp[0][0],
            yv=self.objects.dp[0][1],
            xa=self.objects.ddp[0][0],
            ya=self.objects.ddp[0][1],
            speed=LA.norm(self.objects.dp[0])
        )

    def render(self, tick, ticking):
        self.mainPanel.fill((0, 0, 0))
        self.screen.fill((0, 0, 0))

        surface = self.mainPanel
        self.starfield.render(self.ui.vp.pos, surface)
        self.renderFixedObjects(surface)
        self.renderObjects(surface)

        self.ui.statusBar.render(surface)

        if self.ui.mode == 'menu':
            self.ui.menu.render(surface)

        if ticking and not tick % 3:
            self.minimapPos, self.minimap = self.renderMinimap(self.ui.vp)
            self.infoPanelInfo = self.renderInfoPanel(self.ui.vp)
            self.infoPanel.blit(self.minimap, self.minimapPos)
            self.infoPanel.blit(self.infoPanelInfo, (0, 200))

        self.screen.blit(self.mainPanel, (200, 0))
        self.screen.blit(self.infoPanel, (0, 0))

    def saveState(self, storage):
        # storage.save('enable-gravity', self.enableGravity)
        # if not self.enableGravity:
        #     self.objects.ddp *= 0

        storage.save('objects', self.objects.serialize())
        storage.save('current-sector', tuple(self.currentSector.pos))
        storage.commit()

    def loadState(self, storage):
        storage.connect()
        objects = storage.load('objects')
        if objects is not None:
            self.objects = objects.deserialize(ships.get)
        self.loadSector(sectors.getByPosition(storage.load('current-sector', (0, 0))))
        self.ui.playerShip = self.getMobileController(0)

    def tractor(self, src, weapon):
        if self.objects.gamestate[src].target is not None:
            target = self.objects.gamestate[src].target.index
            a = 10 * (self.objects.p[src] - self.objects.p[target]) / self.objects.gamestate[target].mass
            mag = LA.norm(a)
            if mag > 100:
                a *= 100 / mag
            self.objects.dp[target] += a
            resist = self.objects.gamestate[src].thrust / self.objects.gamestate[src].mass
            mag = LA.norm(a)
            if resist < mag:
                self.objects.dp[src] -= a * (mag - resist)

    def beamCollision(self, src, weapon):
        theta = self.objects.theta[src]
        v = np.array((math.cos(-math.pi * theta / 180), math.sin(-math.pi * theta / 180)))
        vperp = np.array((v[1], -v[0]))
        distance = np.sum(v * (self.objects.p - self.objects.p[src]), axis=1)
        beamDistance = np.abs(np.sum(vperp * (self.objects.p - self.objects.p[src]), axis=1))
        for i, value in enumerate(beamDistance):
            if self.objects.gamestate[i].hitRadius > 0 and distance[i] > 0 and distance[i] < weapon.lifetime and value < 20:
                self.weaponHit(weapon, self.objects.gamestate[i], i)
                # self.objects.gamestate[i].annotation = 'BOOM! (%f)' % distance[i]
            # else:
            #     self.objects.gamestate[i].annotation = None

    def weaponHit(self, weapon, mobile, i):
        damage = weapon.energyPerShot * 2
        if mobile.shieldCharge > 0:
            if mobile.shieldCharge > damage:
                # print 'damage shield'
                mobile.shieldCharge -= damage
                damage = 0
            else:
                # print 'shield offline'
                damage -= mobile.shieldCharge
                mobile.shieldCharge = 0

        if mobile.hullIntegrity < 1:
            self.objects.active[i] = False
            return

        if damage > 0:
            if mobile.hullIntegrity > damage:
                # print 'damage hull'
                mobile.hullIntegrity -= damage
            else:
                # print 'hull breach'
                mobile.hullIntegrity = 0
                self.blowUp(i)
                # destroy

    def blowUp(self, src):
        self.objects.active[src] = False
        n = int(round(10 + random() * 10))
        i = self.objects.add(n, Debris)
        self.objects.p[i:i+n] = self.objects.p[src] + (10 * np.random.random((n, 2)) - 0.5)
        self.objects.dp[i:i+n] = self.objects.dp[src] + 20 * np.random.random((n, 2)) - 10
        self.objects.theta[i:i+n] = 360 * np.random.random(n)
        self.objects.dtheta[i:i+n] = self.objects.dtheta[src] + 40 * np.random.random(n)
        self.objects.active[i:i+n] = True

    def collectGarbage(self):
        k = self.objects.compact()
        if verbose > 2:
            print('Removed %d inactive objects' % k)

    def mapMenu(self, index):
        return (menu.MapMenu, self)

    def dock(self, index):
        if self.fixedObjects.cardinality < 1:
            self.ui.statusBar.notify('There is nothing to dock with.')
            return

        if LA.norm(self.objects.dp[index]) > 20:
            self.ui.statusBar.notify('You are moving too fast to land.')
            return


        distances = LA.norm(self.fixedObjects.p - self.objects.p[index], axis=1)
        closest = np.argmin(distances)
        if distances[closest] < 100:
            return (menu.Menu, DockingMenuModel(self))
        self.ui.statusBar.notify('You are too far away to land.')

    def getMobileController(self, i):
        controller = MobileController(self, self.objects, self.objects.ref(i))
        return controller


class MobileController:
    def __init__(self, game, objects, indexRef):
        self.game = game
        self.objects = objects
        self.indexRef = indexRef
        self.shipType = 'fighter'

    def __getattr__(self, name):
        if name == 'index':
            return self.indexRef.index
        raise AttributeError('%s not in MobileController instance' % name)

    def nextShip(self):
        self.shipType = ships.getNext(self.shipType)
        newShip = ships.get(self.shipType)
        if newShip is None:
            print 'Ship %s not found.' % self.shipType
        self.objects.gamestate[self.index] = ships.get(self.shipType)

    def fire(self, tick):
        sourceIndex = self.index
        mobile = self.objects.gamestate[sourceIndex]
        for w in mobile.weapons:
            if w.lastFired is None or tick - w.lastFired >= w.interval:
                if w.energyPerShot <= mobile.energy:
                    mobile.energy -= w.energyPerShot
                else:
                    # warning: not enough energy
                    continue
                if w.type == 'beam':
                    w.lastFired = tick
                    w.firing = True
                    self.game.beamCollision(0, w)
                elif w.type == 'target-beam':
                    w.lastFired = tick
                    w.firing = True
                    self.game.tractor(0, w)
                elif w.type == 'projectile':
                    w.lastFired = tick
                    i = self.objects.add(1, w.projectile)
                    newMob = self.objects.gamestate[i]
                    newMob.lifetime = w.lifetime
                    newMob.parent = sourceIndex
                    newMob.sourceWeapon = w
                    self.objects.p[i] = self.objects.p[sourceIndex] + (np.random.random(2) - 0.5) * 10
                    etheta = self.objects.theta[sourceIndex] + (random() - 0.5) * w.spread
                    xv = 100 * math.cos(-math.pi * etheta / 180)
                    yv = 100 * math.sin(-math.pi * etheta / 180)
                    vel = np.array([xv, yv]) + self.objects.dp[sourceIndex]
                    self.objects.dp[i] = vel
                    self.objects.theta[i] = etheta
                    # self.objects.dtheta[i] = self.objects.dtheta[i]
                    self.objects.active[i] = True
                    self.objects.canCollide[i] = True

    def accel(self, direction):
        self.objects.ddp[self.index] = np.array((direction * math.cos(-math.pi * self.objects.theta[self.index] / 180), direction * math.sin(-math.pi * self.objects.theta[self.index] / 180))) * self.objects.gamestate[self.index].thrust / self.objects.gamestate[self.index].mass


    def thrust(self, direction, power):
        self.objects.dp[self.index] += power * np.array((direction * math.cos(-math.pi * self.objects.theta[self.index] / 180), direction * math.sin(-math.pi * self.objects.theta[self.index] / 180))) * self.objects.gamestate[self.index].thrust / self.objects.gamestate[self.index].mass

    def decel2(self):
        dp = self.objects.dp[self.index]
        vtheta = -270 + (360 + math.atan2(dp[1], dp[0]) * 180 / math.pi) % 360
        diff = vtheta - self.objects.theta[self.index]
        direction = np.sign(diff)
        print self.objects.theta[self.index], vtheta, direction, abs(diff)
        ddtheta = min(1, abs(diff) / 30) * direction * 40 * self.objects.gamestate[self.index].turnRate / self.objects.gamestate[self.index].mass
        self.objects.ddtheta[self.index] = ddtheta


    def decel(self):
        dp = self.objects.dp[self.index]
        norm = LA.norm(dp)
        if norm > 1:
            dp = np.array(dp)
            dp /= norm
            self.objects.ddp[self.index] = -dp * self.objects.gamestate[self.index].thrust / self.objects.gamestate[self.index].mass
            if LA.norm(self.objects.ddp[self.index]) > LA.norm(self.objects.dp[self.index]) * 10:
                self.objects.dp[self.index] = 0
                self.objects.ddp[self.index] = 0
        else:
            self.objects.dp[self.index] = 0
            self.objects.ddp[self.index] = 0

    def warpHome(self):
        self.objects.p[self.index] = 0

    def turnTo(self, theta, rate = None):
        theta0 = self.objects.theta[self.index] % 360
        theta %= 360

        diff = theta - theta0
        adiff = abs(diff)
        if adiff < 5:
            direction = 0
        else:
            direction = np.sign(diff)
            if adiff > 180:
                direction = -direction
        if rate is None:
            rate = min(1, adiff / 45)
        self.objects.dtheta[self.index] = direction * 40 * rate
        # self.turn(direction)

    def turn(self, direction, rate = None):
        if rate is None:
            rate = 1
        if direction == 0:
            if abs(self.objects.dtheta[self.index]) < -0.1:
                self.objects.ddtheta[self.index] = 0
                self.objects.dtheta[self.index] = 0
            else:
                self.objects.ddtheta[self.index] = -self.objects.dtheta[self.index] * 2
        else:
            self.objects.ddtheta[self.index] = rate * direction * 40 * self.objects.gamestate[self.index].turnRate / self.objects.gamestate[self.index].mass

    def nearestTarget(self):
        dp = self.objects.p - self.objects.p[self.index]
        dp = np.sum(dp * dp, axis=1)
        s = sorted(enumerate(dp), key=lambda t: t[1])
        ref = self.objects.gamestate[self.index].target
        if ref is not None:
            self.objects.gamestate[ref.index].targeted = False
        if len(s) < 2:
            self.objects.gamestate[self.index].target = None
            return
        self.objects.gamestate[self.index].target = self.objects.ref(s[1][0])
        self.objects.gamestate[s[1][0]].targeted = True

    def off(self):
        self.objects.ddp[self.index] = 0
        self.objects.ddtheta[self.index] = 0

class PickleStorage:
    def __init__(self):
        self.data = {}
        pass

    def save(self, name, what):
        self.data[name] = what

    def load(self, name, default = None):
        try:
            return self.data[name]
        except KeyError:
            return default

    def connect(self):
        try:
            with open('world-state.pkl', 'r') as file:
                self.data = pickle.load(file)
        except IOError:
            self.data = {}

    def commit(self):
        with open('world-state.pkl', 'w') as file:
            pickle.dump(self.data, file)

def startGame():
    pg.init()

    screen = pg.display.set_mode(((1024 + 200, 768)))

    ui = UI(vec(1024, 768), vec(512, 384))
    game = Game(ui, screen)

    pg.display.set_caption('Space')

    clock = pg.time.Clock()

    # enemyShip = game.getMobileController(1)
    # enemyAI = enemy.AI(enemyShip, 0)

    # game.loadState(PickleStorage())

    frame = 0
    tick = 0
    framesPerSecond = 30
    ticksPerSecond = 10
    framesPerTick = framesPerSecond / ticksPerSecond

    going = True
    while going:
        test = clock.tick(framesPerSecond)
        frame += 1
        ticking = frame % framesPerTick < 1
        if ticking:
            tick += 1
            if tick % 20 < 1:
                # if not game.objects.active[enemyAI.index]:
                #     game.objects.active[enemyAI.index] = True
                #     game.objects.gamestate[enemyAI.index] = ships.get('fighter')
                #     enemyAI = enemy.AI(enemyAI.mobileController, 0)
                game.collectGarbage()

        game.render(tick, ticking)

        for event in pg.event.get():
            if verbose > 10 and event.type is not MOUSEMOTION:
                print(event)
            ui.handleInputEvent(event)

            if event.type == QUIT:
                going = False
            if ui.quit:
                going = False
            if ui.mode == 'menu':
                pg.display.flip()

        if ui.mode == 'game':
            game.step(tick, ticking)
            # enemyAI.step(frame)
        ui.step(frame, tick)

        # ep.processEvents()
        if ui.mode == 'game':
            pg.display.flip()

    # game.saveState(PickleStorage())




if __name__ == '__main__':
    startGame()
