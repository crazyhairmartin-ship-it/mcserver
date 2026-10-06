"""Draws the Storage Lectern side-tab icons (res/assets/fotfars/textures/gui). Needs Pillow; run in python:3.12-slim."""
from PIL import Image


def lectern_icons():
    """Icons for the Storage Lectern's extra side tabs, in Ars Nouveau's style (cream pixels, drawn over its
    storage_tab1.png tab). One 22x13 tile each: StateButton draws (state * 22, 0, 22, 12)."""
    cream = (255, 250, 238, 255)
    up = ['...#...',
          '..###..',
          '.#.#.#.',
          '...#...',
          '...#...',
          '...#...']
    for name, rows in (('lectern_deposit', up), ('lectern_restock', up[::-1])):
        img = Image.new('RGBA', (22, 13), (0, 0, 0, 0))
        for y, row in enumerate(rows):
            for x, c in enumerate(row):
                if c == '#':
                    img.putpixel((8 + x, 3 + y), cream)
        img.save('res/assets/fotfars/textures/gui/' + name + '.png')


lectern_icons()
print('lectern icons drawn')
