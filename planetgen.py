from random import randint
import subprocess as sp
import tempfile
from PIL import Image
import os

def transparentify(img, color = (255, 255, 255)):
    img = img.convert("RGBA")

    pixdata = img.load()

    color = (color[0], color[1], color[2], 255)

    for y in xrange(img.size[1]):
        for x in xrange(img.size[0]):
            if pixdata[x, y] == color:
                pixdata[x, y] = (255, 255, 255, 0)

    canvas = Image.new('RGBA', img.size, (255,255,255,0)) # Empty canvas colour (r,g,b,a)
    canvas.paste(img, mask=img) # Paste the image onto the canvas, using it's alpha channel as mask
    return canvas

    canvas.thumbnail([width, height], PyImage.ANTIALIAS)

    canvas.save(filename, format="PNG")


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

nameForLabel = {v: k for k, v in labels.iteritems()}

def generate(label, size, outfile, seed = None):
    colorFile = 'planet-generator/colors/%s.col' % nameForLabel[label]
    if seed is None:
        seed = '0.%0d' % randint(0, 2000000000)
    else:
        seed = '0.%0d' % seed
    bigSize = str(int(size * 1024.0 / 200))
    args = ['planet-generator/planet', '-C', colorFile, '-w', bigSize, '-h', bigSize, '-p', 'o', '-s', seed, '-S']

    print 'generating', outfile, '...'
    print '   ', ' '.join(args)
    with tempfile.NamedTemporaryFile(delete=False) as bmp:
        sp.call(args, stdout=bmp)
    img = Image.open(bmp.name)
    img = transparentify(img)
    img.thumbnail((size, size), Image.ANTIALIAS)
    img.save(outfile, format='PNG')
    os.unlink(bmp.name)
