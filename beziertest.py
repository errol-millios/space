import sys
import pygame as pg
import random
import numpy as np
import timeit

def perp(v):
    return np.array([v[1], -v[0]])

def randomPoints():
    p1 = np.array([100, 200], dtype=float)
    p4 = np.array([1024 - 100, 768 - 200], dtype=float)

    v = p4 - p1
    vperp = perp(v / np.linalg.norm(v))

    print v, vperp

    r = (random.random() - 0.5)
    r += 20 * np.sign(r)

    p2 = p1 + v * random.random() + 10 * vperp * r

    r = (random.random() - 0.5)
    r += 20 * np.sign(r)

    p3 = p1 + v * random.random() + 10 * vperp * r

    return np.array([p1, p2, p3, p4])

def B(pts, t):
    s = 1-t
    t2 = t * t
    t3 = t2 * t
    return s * (s * (s * pts[0] + 3 * t * pts[1]) + 3 * t2 * pts[2]) + t3 * pts[3]

def B2(pts, t):
    s = 1-t
    return s**3 * pts[0] + 3 * s**2 * t * pts[1] + 3 * s * t**2 * pts[2] + t**3 * pts[3]


def segments(pts, c, t):
    prev = None
    for p in pts:
        if prev is not None:
            pg.draw.line(screen, c, prev, p, t)
        prev = p


pg.init()
screen = pg.display.set_mode((1024, 768))
screen_rect = screen.get_rect()


pts = randomPoints()

segments(pts, pg.Color('tomato'), 5)

bpts = [B(pts, t) for t in np.arange(0, 1.1, 0.001)]
# print bpts
print B(pts, 0) - pts[0]
print B(pts, 1) - pts[3]

segments(bpts, pg.Color('cyan'), 3)

# rect = pg.Rect(0,0, 300, 100)
# rect.center = screen_rect.center
# pg.draw.rect(screen, pg.Color("tomato"), rect, 20)



pg.display.flip()
n = 1000
print 1000000 * timeit.timeit(""" [B(pts, t) for t in np.arange(0, 1.1, 0.01)] """, setup="import numpy as np\nfrom __main__ import B, pts", number = n) / n
print 1000000 * timeit.timeit(""" [B2(pts, t) for t in np.arange(0, 1.1, 0.01)] """, setup="import numpy as np\nfrom __main__ import B2, pts", number = n) / n


clock = pg.time.Clock()
running = True

while running:
    clock.tick(10)
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                running = False
pg.quit()
sys.exit()
