"""Package screen texture with the mailbox screen's layout: the 5 slot frames moved from the centre to the left
(x 7), leaving room on the right for the recipient box (fotfmail PackageScreenMixin / PackageMenuMixin).

Reads Ender Mail's package.png (pass its path), writes kubejs/assets/endermail/textures/gui/package.png.
Needs Pillow:  python make_package_gui.py path/to/endermail/textures/gui/package.png
"""
import os
import sys

from PIL import Image

PACK = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(PACK, 'kubejs', 'assets', 'endermail', 'textures', 'gui', 'package.png')

img = Image.open(sys.argv[1]).convert('RGBA')
slots = img.crop((43, 19, 133, 37))                      # the 5 slot frames (x 43-132, y 19-36)
background = img.getpixel((150, 28))                     # plain panel colour
for y in range(19, 37):
    for x in range(43, 133):
        img.putpixel((x, y), background)
img.paste(slots, (7, 19))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
img.save(OUT)
img.crop((0, 0, 176, 50)).resize((704, 200), Image.NEAREST).save(os.path.join(os.path.dirname(sys.argv[1]), 'package_gui_preview.png'))
print('package GUI written')
