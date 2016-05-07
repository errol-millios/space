from PIL import Image, ImageFilter
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('infile')
parser.add_argument('outfile')
args = parser.parse_args()

img = Image.open(args.infile)
img = img.convert("RGBA")
data = img.getdata()

newData = []
transparentLocations = set()
for i, item in enumerate(data):
    if item[0] == 255 and item[1] == 255 and item[2] == 255:
        newData.append((255, 255, 255, 0))
        transparentLocations.add(i)
    else:
        newData.append(item)

img.putdata(newData)
img = img.filter(ImageFilter.GaussianBlur(radius=1))

data = img.getdata()

newData = []
for i, item in enumerate(data):
    if i in transparentLocations:
        newData.append((255, 255, 255, 0))
    else:
        newData.append(item)

img.putdata(newData)

# img.save(args.out, "PNG")
# img.thumbnail((200, 200), Image.ANTIALIAS)
img.save(args.outfile)
