"""Map Ars Nouveau's blocks and items to replacements, for fotfskills' RemovedBlocks (plan:
docs/superpowers/specs/2026-10-07-remove-ars-nouveau.md).

    python tools/removed/make_ars_remap.py [path/to/ars_nouveau.jar] [path/to/level.dat]

Archwood becomes Biomes O' Plenty's empyreal wood (recoloured by tools/empyreal/recolor_empyreal.py), including other
mods' archwood variants (Every Compat furniture, Supplementaries sign posts, Snowy Spirit sleds) found in the world's
registry list in level.dat. Sourcestone becomes the stone brick family, Ars machines vanilla look-alikes, and natural
Ars plants vanilla ones; Ars's invisible light blocks, fruit pods, turrets and the like become air. Items: source gems
become amethyst, sourceberries sweet berries, and building blocks follow their block; everything else Ars disappears.
Writes extras/fotfskills/res/fotfskills/removed_ids_ars.txt: `block|item old new [mod that must be gone]`.
"""
import gzip
import re
import sys
import zipfile
from pathlib import Path

PACK = Path(__file__).resolve().parents[2]
OUT = PACK / 'extras' / 'fotfskills' / 'res' / 'fotfskills' / 'removed_ids_ars.txt'
MODS = PACK.parent / 'server' / 'data' / 'mods'
DEFAULT_LEVEL = PACK.parent / 'server' / 'data' / 'world' / 'level.dat'
BOP = 'biomesoplenty:'

SIMPLE = {
    'sourceberry_bush': 'minecraft:sweet_berry_bush', 'magebloom_crop': 'minecraft:wheat',
    'magebloom_block': 'minecraft:pink_wool', 'potted_magebloom_crop': 'minecraft:flower_pot',
    'archwood_chest': 'minecraft:chest', 'archwood_sconce': 'minecraft:lantern', 'sourcestone_sconce': 'minecraft:lantern',
    'polished_sconce': 'minecraft:lantern', 'sconce': 'minecraft:lantern', 'magelight_torch': 'minecraft:torch',
    'storage_lectern': 'minecraft:lectern', 'bookwyrm_lectern': 'minecraft:lectern', 'scribes_table': 'minecraft:lectern',
    'wixie_cauldron': 'minecraft:cauldron', 'ritual_brazier': 'minecraft:campfire', 'brazier_relay': 'minecraft:campfire',
    'source_jar': 'minecraft:glass', 'creative_source_jar': 'minecraft:glass', 'potion_jar': 'minecraft:glass',
    'mob_jar': 'minecraft:glass', 'repository': 'minecraft:barrel', 'source_gem_block': 'minecraft:amethyst_block',
    'falseweave': 'minecraft:white_wool', 'ghostweave': 'minecraft:glass', 'mirrorweave': 'minecraft:white_wool',
    'mage_block': 'minecraft:white_wool', 'sky_block': 'minecraft:glass', 'sourceberry_sack': 'minecraft:brown_wool',
    'whirlisprig_flower': 'minecraft:flowering_azalea', 'drygmy_stone': 'minecraft:mossy_cobblestone',
    'smooth_sourcestone': 'minecraft:smooth_stone', 'smooth_sourcestone_slab': 'minecraft:smooth_stone_slab',
    'smooth_sourcestone_stairs': 'minecraft:stone_stairs', 'sourcestone': 'minecraft:stone_bricks',
    'sourcestone_slab': 'minecraft:stone_brick_slab', 'sourcestone_stairs': 'minecraft:stone_brick_stairs',
}
AIR = ('light_block', 'temporary_block', 'temporary_light_block', 'intangible_air', 'redstone_air', 'magic_fire', 'portal',
       'rune', 'ritual', 'bastion_pod', 'bombegranate_pod', 'mendosteen_pod', 'frostaya_pod', 'spell_prism', 'void_prism',
       'spell_sensor', 'item_detector', 'source_gem')
ITEMS = {'source_gem': 'minecraft:amethyst_shard', 'sourceberry_bush': 'minecraft:sweet_berries',
         'magebloom': 'minecraft:pink_dye', 'magebloom_fiber': 'minecraft:string', 'wilden_wing': 'minecraft:feather',
         'wilden_horn': 'minecraft:bone', 'wilden_spike': 'minecraft:bone', 'worn_notebook': 'minecraft:book'}


def archwood_target(b):
    """Archwood pieces -> the empyreal piece of the same shape."""
    m = re.fullmatch(r'(stripped_)?(?:(?:red|blue|green|purple)_)?archwood_(log|wood)', b)
    if m:
        return f'{BOP}{m.group(1) or ""}empyreal_{m.group(2)}'
    m = re.fullmatch(r'(potted_)?(?:red|blue|green|purple)_archwood_(leaves|sapling)', b)
    if m:
        return f'{BOP}{m.group(1) or ""}empyreal_{m.group(2)}'
    m = re.fullmatch(r'archwood_(planks|slab|stairs|fence|fence_gate|door|trapdoor|button|pressure_plate|sign|wall_sign)', b)
    if m:
        return f'{BOP}empyreal_{m.group(1)}'
    return None


def block_target(b):
    if b in SIMPLE:
        return SIMPLE[b]
    if b in AIR:
        return 'minecraft:air'
    t = archwood_target(b)
    if t:
        return t
    m = re.fullmatch(r'(?:smooth_)?(?:gilded_)?sourcestone_\w+?(_slab|_stairs)?', b)
    if m:
        shape = m.group(1) or ''
        return {'': 'minecraft:chiseled_stone_bricks' if 'gilded' in b else 'minecraft:stone_bricks',
                '_slab': 'minecraft:stone_brick_slab', '_stairs': 'minecraft:stone_brick_stairs'}[shape]
    if re.search(r'_sbed$', b):
        return 'minecraft:white_bed' if b.startswith(('white', 'yellow', 'orange')) else 'minecraft:red_bed'
    if re.search(r'turret|sourcelink|relay|apparatus|arcane_|imbuement|alteration|crystallizer|scryers|potion_', b):
        return 'minecraft:smooth_stone'
    return 'minecraft:stone_bricks'


def variant_lines(level):
    """Other mods' blocks made in archwood (everycomp:hc/ars_nouveau/archwood_chair...) -> their empyreal versions."""
    ids = set(m.decode() for m in re.findall(rb'[a-z][a-z0-9_.-]*:[a-z0-9_/.-]+', gzip.open(level).read()))
    lines = []
    for i in sorted(x for x in ids if 'ars_nouveau/' in x and not x.startswith('ars_nouveau:')):
        t = i.replace('ars_nouveau/', 'biomesoplenty/').replace('archwood', 'empyreal')
        t = re.sub(r'(?:red|blue|green|purple)_empyreal_shrub$', 'empyreal_shrub', t)
        if t in ids:
            lines += [f'block {i} {t} ars_nouveau', f'item {i} {t} ars_nouveau']
    return lines


def main():
    jar = Path(sys.argv[1]) if len(sys.argv) > 1 else next(MODS.glob('ars_nouveau*.jar'))
    level = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_LEVEL
    z = zipfile.ZipFile(jar)
    blocks = sorted({n.split('/')[-1][:-5] for n in z.namelist()
                     if n.startswith('assets/ars_nouveau/blockstates/') and n.endswith('.json')})
    lines = [f'block ars_nouveau:{b} {block_target(b)}' for b in blocks]
    for b in blocks:                                        # block items follow their block, unless air
        t = ITEMS.get(b, block_target(b))
        if t != 'minecraft:air' and not b.endswith('wall_sign') and not b.startswith('potted_'):
            lines.append(f'item ars_nouveau:{b} {t}')
    for i, t in ITEMS.items():
        if i not in blocks:
            lines.append(f'item ars_nouveau:{i} {t}')
    extra = variant_lines(level) if level.exists() else []
    lines += extra
    OUT.write_text('# old id -> replacement [mod that must be gone], made by tools/removed/make_ars_remap.py\n'
                   + '\n'.join(lines) + '\n', encoding='utf-8')
    print(f'{len(blocks)} Ars blocks, {len(extra) // 2} other-mod archwood variants -> {OUT.relative_to(PACK)}')


if __name__ == '__main__':
    main()
