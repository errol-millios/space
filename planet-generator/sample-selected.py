import os
import glob
import subprocess as sp
import numpy as np
from PIL import Image
import matplotlib.colors

from util import parseFilename, transparentify

labels = {
    '148095main_PIA08118-516': 'desert-1',
    '20150104_145414': 'ice',
    '20150106_235115': 'moss',
    '20150106_235733': 'raddichio',
    '20150106_235742': 'sepia-1',
    '20150107_181106_Richtone(HDR)': 'mud-lava',
    '20150108_004832': 'sepia-2',
    '20150110_122248': 'barren-1',
    '20150502_165519': 'swamp',
    '20150517_153615': 'jungle-1',
    '20150606_140018': 'boreal',
    '20150607_120632': 'forest',
    '20150718_140141': 'ocean-1',
    '20150718_140152': 'ocean-2',
    'bright-cloud': 'cloudy-1',
    'carlsagan': 'jungle-2',
    'img048_2': 'forest-grassland',
    'img050_2': 'grassland',
    'img052_2': 'hardscrabble',
    'img054_2': 'desert-2',
    'img078_2': 'archipelago-1',
    'img090_2': 'barren-2',
    'img136_2': 'archipelago-2',
    'img1227': 'desert-3',
    'Mars_atmosphere_2': 'mars',
    'Richard-Feynman-Messenger-Lectures-': 'barren-3',
    'rimg2280': 'muddy',
    'rimg2544_3': 'barren-4',
    'rimg2555': 'dirt',
    'Uranus,_Earth_size_comparison_2': 'cloudy-4',
    'Venus_Clouds': 'desert-4',
    'WDF_2020099': 'cloudy-2',
    'WDF_2669099': 'cloudy-3'
}

if len(set(labels.values())) != len(labels):
    print 'Non-unique label encountered.'
    exit()



colorCache = {}

def loadColors(filename):
    if filename not in colorCache:
        with open(filename, 'r') as file:
            colorCache[filename] = np.array([tuple(map(int, t)) for t in [line.strip().split(' ') for line in file] if len(t) == 4])
    return colorCache[filename]

def varyColors(filename):
    colors = loadColors(filename)
    N = colors.shape[0] - 6
    r = np.random.random((N, 3)) * 0.4 + 0.8
    result = np.array(colors)
    result[6:,1:] = np.clip(result[6:,1:] * r, 0, 255)
    return result

def sortByHue(filename):
    colors = loadColors(filename)
    colors = sorted(colors, key=lambda c: matplotlib.colors.rgb_to_hsv(c[1:])[0])
    for i, c in enumerate(colors):
        colors[i][0] = i
    return colors

def colorsToString(colors):
    return '\n'.join(map(lambda c: '%d %d %d %d' % tuple(c), colors))

white = (255, 255, 255, 255)

selected = glob.glob('selected/*')

names = [parseFilename(fn)
         for fn in selected]

parameters = [(
    'colors/%s.col' % n[0], '0.%s' % str(seed),
    'high-quality/%s.%s.bmp' % (labels[n[0]], seed),
    'high-quality/%s.%s.png' % (labels[n[0]], seed),
    'high-quality/small-%s.%s.png' % (labels[n[0]], seed))
              for n in names for seed in np.random.random_integers(2000000000, size=10)]

# for color, seed, outfile, smalloutfile in parameters:
#     print loadColors(color)
#     print varyColors(color)
#     print colorsToString(sortByHue(color))
#     exit()

argsList = [(['./planet', '-C', colorFile, '-w', '200', '-h', '200', '-p', 'o', '-s', seed], colorFile, outfile, pngoutfile, smalloutfile)
            for colorFile, seed, outfile, pngoutfile, smalloutfile in parameters]

sortColorsByHue = False

for args, colorFile, outfile, pngoutfile, smalloutfile in argsList:
    if not os.path.isfile(outfile):
        print ' '.join(args), '>', outfile
        if sortColorsByHue:
            with open(outfile, 'w') as fp:
                proc = sp.Popen(args, stdin=sp.PIPE, stdout=fp)
                proc.stdin.write(colorsToString(sortByHue(colorFile)))
                proc.stdin.close()
        else:
            with open(outfile, 'w') as fp:
                sp.call(args, stdout=fp)
    if not os.path.isfile(pngoutfile):
        print 'producing PNG'
        img = Image.open(outfile)
        img.save(pngoutfile, format='PNG')
        del img
    if False and not os.path.isfile(smalloutfile):
        print 'producing sprite'
        img = Image.open(outfile)
        img = transparentify(img, white)
        img.thumbnail((200, 200), Image.ANTIALIAS)
        img.save(smalloutfile, format='PNG')
        del img
