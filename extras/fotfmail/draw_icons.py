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


def hat():
    """64x32 texture for MailHatLayer: crown UV (0,0) 9x3x9, visor (0,12) 9x0.5x3, badge (0,17) 2x2x0.25."""
    navy, navy_dark, band, visor, gold, gold_dark = (
        (44, 58, 104, 255), (32, 42, 78, 255), (70, 92, 150, 255), (22, 22, 28, 255), (232, 190, 64, 255), (176, 132, 36, 255))
    img = Image.new('RGBA', (64, 32), CLEAR)
    px = img.load()
    for y in range(0, 12):           # crown: top/bottom faces in rows 0-8, sides in rows 9-11
        for x in range(0, 36):
            px[x, y] = navy if y < 9 else (band if y == 11 else navy)
    for x in range(0, 36, 3):        # a little texture on the top
        px[x, 4] = navy_dark
    for y in range(12, 16):          # visor
        for x in range(0, 24):
            px[x, y] = visor
    for y in range(17, 20):          # badge
        for x in range(0, 6):
            px[x, y] = gold
    px[1, 18] = gold_dark
    img.save('res/assets/fotfmail/textures/entity/mail_hat.png')


hat()
print('hat drawn')


def stamp():
    """16x16 generic postage stamp, replacing Ender Mail's stamp icon (kubejs/assets/endermail/textures/item)."""
    paper, paper_shade, border = (246, 238, 214, 255), (214, 202, 172, 255), (178, 52, 48, 255)
    sky, sky_light, sun, hill, hill_dark, trunk, leaf = (
        (120, 176, 228, 255), (156, 202, 240, 255), (250, 214, 84, 255), (98, 168, 76, 255), (70, 132, 56, 255),
        (112, 78, 46, 255), (54, 112, 52, 255))
    img = Image.new('RGBA', (16, 16), CLEAR)
    px = img.load()
    for y in range(1, 15):            # stamp paper
        for x in range(1, 15):
            px[x, y] = paper
    for i in range(1, 15, 2):         # perforated edges: every other edge pixel cut away
        px[i, 1] = px[i, 14] = px[1, i] = px[14, i] = CLEAR
    for i in range(2, 14):            # shading on the bottom/right edges
        if px[i, 13][3]:
            px[i, 13] = paper_shade
        if px[13, i][3]:
            px[13, i] = paper_shade
    for i in range(3, 13):            # red frame
        px[i, 3] = px[i, 12] = px[3, i] = px[12, i] = border
    for y in range(4, 12):            # picture: sky
        for x in range(4, 12):
            px[x, y] = sky_light if y < 6 else sky
    for x, y in ((9, 5), (10, 5), (9, 6), (10, 6)):   # sun
        px[x, y] = sun
    for x in range(4, 12):            # rolling hill
        top = 9 if x in (4, 5, 10, 11) else 8
        for y in range(top, 12):
            px[x, y] = hill if y == top else hill_dark
    px[6, 7] = px[6, 6] = leaf        # little tree
    px[5, 7] = px[7, 7] = leaf
    px[6, 8] = trunk
    img.save(STAMP_OUT)


STAMP_OUT = '../../kubejs/assets/endermail/textures/item/stamp.png'
stamp()
print('stamp drawn')


def letter_gui():
    """256x256 letter paper for the book screens when the item is a Letter (fotfmail BookEditScreenMixin /
    BookViewScreenMixin). Only the 192x192 corner is drawn, in the same place as the vanilla book page."""
    img = Image.new('RGBA', (256, 256), CLEAR)
    px = img.load()
    paper, paper_edge, rule, margin = (250, 244, 228, 255), (220, 210, 186, 255), (176, 200, 228, 255), (226, 140, 140, 255)
    red, blue = (206, 52, 52, 255), (52, 90, 178, 255)
    x0, y0, x1, y1 = 22, 4, 164, 180
    for y in range(y0, y1):
        for x in range(x0, x1):
            px[x, y] = paper
    for x in range(x0, x1):                       # edges
        px[x, y0] = px[x, y1 - 1] = paper_edge
    for y in range(y0, y1):
        px[x0, y] = px[x1 - 1, y] = paper_edge
    for i, (x, y) in enumerate(                   # airmail border: red and blue dashes all the way round
            [(x, y0 + 2) for x in range(x0 + 2, x1 - 2)] + [(x1 - 3, y) for y in range(y0 + 2, y1 - 2)]
            + [(x, y1 - 3) for x in range(x1 - 3, x0 + 1, -1)] + [(x0 + 2, y) for y in range(y1 - 3, y0 + 1, -1)]):
        colour = red if (i // 4) % 2 == 0 else blue
        px[x, y] = colour
        if (i // 4) % 2 == 0:
            pass
    for line in range(14):                        # ruled lines under each 9px line of text (text starts at y 32)
        y = 32 + 9 * line + 8
        if y >= y1 - 8:
            break
        for x in range(34, 152):
            px[x, y] = rule
    for y in range(12, y1 - 8):                   # margin line
        px[31, y] = margin
    img.save('res/assets/fotfmail/textures/gui/letter.png')
    img.crop((0, 0, 192, 192)).resize((384, 384), Image.NEAREST).save('letter_gui_preview.png')


letter_gui()
print('letter paper drawn')
