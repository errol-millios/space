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
