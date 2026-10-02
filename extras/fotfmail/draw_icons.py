"""Draws the 16x16 letter icons (res/assets/fotfmail/textures/item). Needs Pillow; run in python:3.12-slim."""
from PIL import Image

OUT = 'res/assets/fotfmail/textures/item/'
CLEAR = (0, 0, 0, 0)
PAPER, PAPER_SHADE, EDGE = (245, 238, 214, 255), (222, 210, 178, 255), (150, 128, 92, 255)
INK = (92, 104, 140, 255)
ENVELOPE, ENVELOPE_SHADE, FLAP = (236, 222, 190, 255), (206, 188, 150, 255), (220, 204, 168, 255)
WAX, WAX_DARK, WAX_LIGHT = (196, 40, 44, 255), (140, 24, 30, 255), (236, 96, 90, 255)
FEATHER, FEATHER_SHADE, QUILL = (250, 250, 250, 255), (200, 205, 215, 255), (90, 70, 50, 255)


def letter():
    img = Image.new('RGBA', (16, 16), CLEAR)
    px = img.load()
    for y in range(2, 15):           # sheet of paper
        for x in range(3, 12):
            px[x, y] = PAPER
    for y in range(2, 15):
        px[3, y] = px[11, y] = EDGE
    for x in range(3, 12):
        px[x, 2] = px[x, 14] = EDGE
    for x in range(10, 12):          # folded corner
        px[x, 3] = PAPER_SHADE
    px[11, 2] = CLEAR
    for y, (x0, x1) in zip((5, 7, 9, 11), ((5, 9), (5, 10), (5, 10), (5, 8))):   # written lines
        for x in range(x0, x1):
            px[x, y] = INK
    feather = [(13, 1), (12, 2), (13, 2), (12, 3), (13, 3), (14, 3), (11, 4), (12, 4), (13, 4), (11, 5), (12, 5)]
    for x, y in feather:             # quill feather
        px[x, y] = FEATHER
    for x, y in ((14, 2), (13, 5), (12, 6)):
        px[x, y] = FEATHER_SHADE
    for x, y in ((10, 7), (9, 8), (8, 9)):
        px[x, y] = QUILL
    img.save(OUT + 'letter.png')


def sealed():
    img = Image.new('RGBA', (16, 16), CLEAR)
    px = img.load()
    for y in range(4, 13):           # envelope body
        for x in range(1, 15):
            px[x, y] = ENVELOPE
    for y in range(4, 13):
        px[1, y] = px[14, y] = EDGE
    for x in range(1, 15):
        px[x, 4] = px[x, 12] = EDGE
    for i in range(7):               # flap: a V from the top corners to the middle
        for x in range(2 + i, 14 - i):
            px[x, 5 + i] = FLAP if i < 4 else px[x, 5 + i]
        px[2 + i, 5 + i] = px[13 - i, 5 + i] = ENVELOPE_SHADE
    for x, y in ((6, 8), (7, 8), (8, 8), (9, 8), (6, 9), (7, 9), (8, 9), (9, 9), (7, 7), (8, 7), (7, 10), (8, 10)):
        px[x, y] = WAX               # wax seal
    for x, y in ((6, 9), (7, 10), (8, 10), (9, 9)):
        px[x, y] = WAX_DARK
    px[7, 8] = WAX_LIGHT
    img.save(OUT + 'letter_signed.png')


letter()
sealed()
print('icons drawn')
