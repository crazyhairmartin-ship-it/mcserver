"""Map Tinkers' Construct's natural blocks (slime islands, slime geodes, cobalt ore) to vanilla blocks, for fotfskills'
RemovedBlocks.

    python tools/removed/make_tinkers_remap.py [path/to/TConstruct.jar]

Reads the block ids from the Tinkers jar (default: the live server's mods folder) and writes
extras/fotfskills/res/fotfskills/removed_ids.txt, one `block|item old_id new_id` per line. fotfskills adds these as
permanent registry aliases once Tinkers is gone, so slime islands turn into vanilla ones instead of floating holes.
Only natural blocks are mapped (and their items, so a stack in a chest keeps its block); everything players built or
made from Tinkers (seared bricks, glass, tools, Every Compat furniture in slime woods) disappears.
"""
import re
import sys
import zipfile
from pathlib import Path

PACK = Path(__file__).resolve().parents[2]
OUT = PACK / 'extras' / 'fotfskills' / 'res' / 'fotfskills' / 'removed_ids.txt'
DEFAULT_JAR = PACK.parent / 'server' / 'data' / 'mods' / 'TConstruct-1.20.1-3.12.1.231.jar'

WOODS = {'greenheart': 'jungle', 'skyroot': 'birch', 'bloodshroom': 'crimson', 'enderbark': 'mangrove'}
# slime colour -> (leaves, sapling, tall grass, fern)
SLIME = {'earth': ('jungle_leaves', 'jungle_sapling', 'grass', 'fern'),
         'sky': ('azalea_leaves', 'birch_sapling', 'grass', 'fern'),
         'ender': ('mangrove_leaves', 'mangrove_propagule', 'air', 'air'),
         'blood': ('nether_wart_block', 'crimson_fungus', 'crimson_roots', 'crimson_roots'),
         'ichor': ('shroomlight', 'crimson_fungus', 'crimson_roots', 'crimson_roots')}
# slime dirt -> (grass, dirt): the ender islands float in the End, the ichor ones in the Nether
DIRT = {'vanilla': ('grass_block', 'dirt'), 'earth': ('grass_block', 'dirt'), 'sky': ('grass_block', 'dirt'),
        'ichor': ('crimson_nylium', 'netherrack'), 'ender': ('end_stone', 'end_stone')}


def natural_target(b):
    """The vanilla block for a natural Tinkers block, or None for anything players build."""
    m = re.fullmatch(r'(greenheart|skyroot|bloodshroom|enderbark)_(log|wood)', b)
    if m:
        wood = WOODS[m.group(1)]
        part = {'log': 'stem', 'wood': 'hyphae'}[m.group(2)] if wood == 'crimson' else m.group(2)
        return f'{wood}_{part}'
    if b == 'enderbark_roots':
        return 'mangrove_roots'
    if re.fullmatch(r'\w+_enderbark_roots', b):
        return 'muddy_mangrove_roots'
    m = re.fullmatch(r'(\w+?)_(\w+?)_slime_grass', b)      # <grass colour>_<dirt>_slime_grass
    if m and m.group(2) in DIRT:
        return DIRT[m.group(2)][0]
    m = re.fullmatch(r'(earth|sky|ichor|ender)_slime_dirt', b)
    if m:
        return DIRT[m.group(1)][1]
    m = re.fullmatch(r'(earth|sky|ender|blood|ichor)_slime_(leaves|sapling|tall_grass|fern|vine)', b)
    if m:
        leaves, sapling, grass, fern = SLIME[m.group(1)]
        return {'leaves': leaves, 'sapling': sapling, 'tall_grass': grass, 'fern': fern, 'vine': 'vine'}[m.group(2)]
    if re.fullmatch(r'(earth|sky|ender|blood|ichor)_(congealed_slime|slime)', b):
        return 'slime_block'
    if re.fullmatch(r'\w+_slime_fluid', b):
        return 'water'
    if 'slime_crystal' in b:
        if b.startswith('budding') or b.endswith('_block'):
            return 'amethyst_block'                     # plain blocks: no free amethyst farm
        if b.endswith('_cluster'):
            return 'amethyst_cluster'
        return re.match(r'(small|medium|large)', b).group(1) + '_amethyst_bud'
    if re.fullmatch(r'(cobalt|steel|knightmetal)_cluster', b):
        return 'amethyst_cluster'
    if b == 'cobalt_ore':
        return 'nether_gold_ore'
    return None


def main():
    jar = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_JAR
    blocks = sorted({n.split('/')[-1][:-5] for n in zipfile.ZipFile(jar).namelist()
                     if n.startswith('assets/tconstruct/blockstates/') and n.endswith('.json')})
    mapped = {b: t for b in blocks if (t := natural_target(b))}
    lines = [f'block tconstruct:{b} minecraft:{t}' for b, t in mapped.items()]
    lines += [f'item tconstruct:{b} minecraft:{t}' for b, t in mapped.items() if t not in ('air', 'water')]
    OUT.write_text('# old id -> replacement, made by tools/removed/make_tinkers_remap.py\n' + '\n'.join(lines) + '\n',
                   encoding='utf-8')
    print(f'{len(mapped)} of {len(blocks)} Tinkers blocks are natural and mapped -> {OUT.relative_to(PACK)}')


if __name__ == '__main__':
    main()
