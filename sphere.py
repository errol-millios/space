import pygame as pg
import sys
import numpy as np
from scipy import misc

# image = pg.image.load('worldgen/foo.gif')

# pg.init()
# screen = pg.display.set_mode((1024, 640))
# screen_rect = screen.get_rect()


# screen.blit(image, (0, 0))
# pg.display.flip()


data = np.fromfile('worldgen/world.raw', dtype=np.dtype('i4'))
print data.shape

image = np.reshape(data, (1280, 640)).T

misc.imsave('outraw.png', misc.imresize(image, (160, 320)))

exit()

image = misc.imread('worldgen/foo.gif')

palette = np.transpose(np.array([
    [0,0,0,0,0,0,0,0,34,68,102,119,136,153,170,187,0,34,34,119,187,255,238,
     221,204,187,170,153,136,119,85,68,255,250,245,240,235,230,225,220,215,
     210,205,200,195,190,185,180,175],
    [0,0,17,51,85,119,153,204,221,238,255,255,255,255,255,255,68,102,136,
     170,221,187,170,136,136,102,85,85,68,51,51,34,255,250,245,240,235,
     230,225,220,215,210,205,200,195,190,185,180,175],
    [0,68,102,136,170,187,221,255,255,255,255,255,255,
     255,255,255,0,0,0,0,0,34,34,34,34,34,34,34,34,34,
     17,0,255,250,245,240,235,230,225,220,215,210,205,
     200,195,190,185,180,175]
], dtype=float))

print len(set(map(tuple, list(palette)))), 'distinct colors'


# ar = np.array(np.transpose(pg.surfarray.array2d(image)), dtype=float)

ar = image

print (image.shape[0], image.shape[1], 3)

output = np.zeros((image.shape[0], image.shape[1], 3), dtype=float)

print image.shape
print output.shape
print output[0][0]

for i, row in enumerate(image):
    for j, pixel in enumerate(row):
        output[i][j] = palette[pixel]

output = np.average(output, axis=2)

misc.imsave('outbw.png', output)

# out = np.array((size, size))

# for i in xrange(size):
#     for j in xrange(size):
#         x = i - half
#         y = j - half
#         if x * x + y * y < radius:



# clock = pg.time.Clock()
# running = True

# while running:
#     clock.tick(10)
#     for event in pg.event.get():
#         if event.type == pg.QUIT:
#             running = False
#         elif event.type == pg.KEYDOWN:
#             if event.key == pg.K_ESCAPE:
#                 running = False
# pg.quit()
# sys.exit()
