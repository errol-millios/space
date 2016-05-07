import pygame as pg
import numpy as np

vec = lambda *a: np.array(a)
def B(pts, t):
    s = 1-t
    t2 = t * t
    t3 = t2 * t
    return s * (s * (s * pts[0] + 3 * t * pts[1]) + 3 * t2 * pts[2]) + t3 * pts[3]

def B2(pts, t):
    s = 1-t
    return s**3 * pts[0] + 3 * s**2 * t * pts[1] + 3 * s * t**2 * pts[2] + t**3 * pts[3]

def perp(v):
    return np.array([v[1], -v[0]])


def spline(p1, p4, rs):
    v = p4 - p1
    vperp = perp(v / np.linalg.norm(v))

    r = (rs[0] - 0.5)
    r += np.sign(r)

    p2 = p1 + v * rs[1] + 10 * vperp * r

    r = (rs[2] - 0.5)
    r += np.sign(r)

    p3 = p1 + v * rs[3] + 10 * vperp * r

    pts = [p1, p2, p3, p4]

    d = 0.1
    a = d
    b = 1

    return [B(pts, t) for t in np.arange(a, b, d)]


def _spline(p1, p4):
    v = p4 - p1
    vperp = perp(v / np.linalg.norm(v))

    r = (random() - 0.5)
    r += np.sign(r)

    p2 = p1 + v * random() + 10 * vperp * r

    r = (random() - 0.5)
    r += np.sign(r)

    p3 = p1 + v * random() + 10 * vperp * r

    pts = [p1, p2, p3, p4]

    d = 0.1
    a = d
    b = 1

    return [B(pts, t) for t in np.arange(a, b, d)]

def generate(specs):
    bw = specs[0]
    bl = specs[1]
    nw = specs[2]
    nl = specs[3]
    wl = specs[4]
    wsf = specs[5]
    wsb = specs[6]
    ww = specs[7]
    tw = specs[8]
    tl = specs[9]

    splined = specs[10:]

    a = vec(bw / 2, bl / 2)
    b = a + [(-bw + nw) / 2, nl]
    c = a - (-wl, wsf)
    d = c - (0, ww)
    e = d - (wl, wsb)
    f = e - ((bw - tw)/2, tl)

    seq = [b, a, c, d, e, f]

    points = []

    skeletonPoints = []

    i = 0
    prev = None
    for p in seq:
        if prev is not None:
            if splined[i * 5] < 0.5:
                points += spline(prev, p, splined[i * 5:(i + 1) * 5])
            i += 1
        points.append(p)
        skeletonPoints.append(p)
        prev = p


    points += list(reversed(vec(*points) * (-1, 1)))
    points = vec(*points)

    skeletonPoints += list(reversed(vec(*points) * (-1, 1)))
    skeletonPoints = vec(*skeletonPoints)

    pmin = points.min(axis=0)
    pmax = points.max(axis=0)

    divisor = (pmax - pmin).max()

    skeletonPoints /= divisor
    points /= divisor

    return points - skeletonPoints.mean(axis=0)

def renderShip(ship, surface):
    pg.draw.polygon(surface, pg.Color('tomato'), ship)
