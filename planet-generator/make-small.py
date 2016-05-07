from PIL import Image
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('infile')
parser.add_argument('outfile')
args = parser.parse_args()
img = Image.open(args.infile)
if img.size[0] < 50 or img.size[1] < 50:
    print 'Refusing to process image %s with size %s.' % (args.infile, img.size)
    exit()
if img.size[0] > 400 or img.size[1] > 400:
    print '%s: resized' % args.infile
    img.thumbnail((400, 400), Image.ANTIALIAS)
else:
    print '%s: original size' % args.infile
img.save(args.outfile)
