"""Shorter flames for the Ultimate Unicorn Mod's Nightmare hoof fire (only that fire; normal fire is untouched).

The Nightmare fire block reuses vanilla's fire models. This writes its own copies with the floor and side flames at
HEIGHT_SCALE of vanilla's 22.4px height (texture squished to fit), and points the block at them:
  kubejs/assets/ultimate_unicorn_mod/models/block/short_fire_*.json
  kubejs/assets/ultimate_unicorn_mod/blockstates/nightmare_fire_block.json
Reads vanilla's templates and the mod's blockstate from the Prism client jar / server mods folder (paths below).
"""
import glob
import json
import os
import zipfile

HEIGHT_SCALE = 0.4  # 22.4px * 0.4 = 9px: barely over half a block
CLIENT_JAR = 'C:/Users/Dylan/AppData/Roaming/PrismLauncher/libraries/com/mojang/minecraft/1.20.1/minecraft-1.20.1-client.jar'
MOD_JAR = glob.glob('C:/Users/Dylan/Documents/Minecraft server/server/data/mods/ultimate_unicorn_mod-*.jar')[0]
PACK = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(PACK, 'kubejs', 'assets', 'ultimate_unicorn_mod')

client = zipfile.ZipFile(CLIENT_JAR)


def vanilla(name):
    return json.loads(client.read(f'assets/minecraft/models/block/{name}.json'))


def write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        json.dump(obj, f, indent=1)


for template in ('template_fire_floor', 'template_fire_side', 'template_fire_side_alt'):
    model = vanilla(template)
    for element in model['elements']:
        element['to'][1] = round(element['to'][1] * HEIGHT_SCALE, 3)
    write(os.path.join(OUT, 'models', 'block', template.replace('template_fire', 'template_short_fire') + '.json'), model)

renamed = {}
for kind in ('floor', 'side', 'side_alt', 'up', 'up_alt'):
    for i in (0, 1):
        name = f'fire_{kind}{i}'
        model = vanilla(name)
        if kind in ('floor', 'side', 'side_alt'):
            model['parent'] = f'ultimate_unicorn_mod:block/template_short_fire_{kind}'
        write(os.path.join(OUT, 'models', 'block', f'short_{name}.json'), model)
        renamed[f'minecraft:block/{name}'] = f'ultimate_unicorn_mod:block/short_{name}'

blockstate = json.loads(zipfile.ZipFile(MOD_JAR).read('assets/ultimate_unicorn_mod/blockstates/nightmare_fire_block.json'))
text = json.dumps(blockstate, indent=1)
for old, new in renamed.items():
    text = text.replace(f'"{old}"', f'"{new}"')
write(os.path.join(OUT, 'blockstates', 'nightmare_fire_block.json'), json.loads(text))
print('short Nightmare fire written:', len(renamed), 'models')
