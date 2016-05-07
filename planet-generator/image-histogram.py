import sys
import numpy as np
from scipy import misc
import argparse

import colorsys

def lum(t):
    return 0.2126 * t[0] + 0.7152 * t[1] + 0.0722 * t[2]

def notWacky(t):
    h, s, v = colorsys.rgb_to_hsv(t[0] / 256.0, t[1] / 256.0, t[2] / 256.0)
    return v < 0.99 and s < 0.99

if False:
    data = np.zeros((512, 512, 3))
    print data.shape
    for i in xrange(data.shape[0]):
        for j in xrange(data.shape[1]):
            c = i * 512 + j
            r = int(c % 64) * 4
            g = int((c / 64) % 64) * 4
            b = int((c / 64 / 64) % 64) * 4
            p = (r, g, b)
            data[i][j] = p
            if notWacky(p):
                data[i][j] = p
            else:
                data[i][j] = (0, 0, 0)

    misc.imsave('wackytest.png', data)
    exit()




parser = argparse.ArgumentParser()
parser.add_argument('infile')
args = parser.parse_args()

image = misc.imread(args.infile)

colorCounts = {}

for i in xrange(image.shape[0]):
    for j in xrange(image.shape[1]):
        c = tuple((image[i][j] + 1) / 4)
        if c not in colorCounts:
            colorCounts[c] = 1
        else:
            colorCounts[c] += 1


prefix = """
0 0 0 0
1 255 255 255
2 255 255 255
3 0 0 0
4 0 0 0
5 255 0 0
"""

print prefix


wackyRemoved = filter(lambda e: notWacky(e[0]), colorCounts.items())

top256 = sorted(wackyRemoved, key=lambda e: -e[1])[:256]
colors = sorted(top256, key=lambda e: lum(e[0]))

for i, result in enumerate(colors):
    print "%d %d %d %d" % (i + 6, result[0][0] * 4, result[0][1] * 4, result[0][2] * 4)

# misc.imsave(outfile, output)

if False:
    test = [
        (255, 255, 0),
        (255, 0, 255),
        (0, 255, 255),
        (0, 0, 255),
        (0, 255, 0),
        (255, 0, 0),
        (128, 128, 128),
        (128, 128, 0),
        (128, 0, 0),
        (0, 0, 0),
    ]

    print map(notWacky, test)
