import os
import glob
import subprocess as sp
from PIL import Image

def parseFilename(f):
    pos = f.rfind('/')
    name = f[1+pos:]

    parts = name.split('.')

    if len(parts) != 3:
        return None

    return parts[0], parts[1]


def transparentify(img, color):
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

white = (255, 255, 255, 255)

selected = glob.glob('selected/*')

names = [parseFilename(fn)
         for fn in selected]

parameters = [('colors/%s.col' % n[0],'0.%s' % n[1], 'high-quality/%s.png' % n[0], 'high-quality/small-%s.png' % n[0])
              for n in names]

argsList = [(['./planet', '-C', color, '-w', '1024', '-h', '1024', '-p', 'o', '-s', seed], outfile, smalloutfile)
            for color, seed, outfile, smalloutfile in parameters]

for args, outfile, smalloutfile in argsList:
    if not os.path.isfile(outfile):
        print ' '.join(args), '>', outfile
        with open(outfile, 'w') as fp:
            sp.call(args, stdout=fp)
    if not os.path.isfile(smalloutfile):
        print 'producing sprite'
        img = Image.open(outfile)
        img = transparentify(img, white)
        img.thumbnail((200, 200), Image.ANTIALIAS)
        img.save(smalloutfile, format='PNG')
