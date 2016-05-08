from random import randint
import subprocess as sp
import tempfile
from PIL import Image
import os

import yaml

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


_planetTypes = None
with open('resources/planet-types.yaml', 'r') as file:
    _planetTypes = yaml.load(file.read())

if len(set([t['label'] for t in _planetTypes.values()])) != len(_planetTypes):
    print 'Non-unique label encountered.'
    exit()

nameForLabel = {v['label']: k for k, v in _planetTypes.iteritems()}

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
