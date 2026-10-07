"""Map every Tinkers' Construct block and item to a vanilla (or in-pack) replacement, for fotfskills' RemovedBlocks.

    python tools/removed/make_tinkers_remap.py [path/to/TConstruct.jar] [path/to/level.dat]

Reads the block and item ids from the Tinkers jar (default: the live server's mods folder), plus Every Compat's
Tinkers-wood furniture ids from the world's registry list in level.dat (each goes to the same mod's jungle, birch,
crimson or mangrove version), and writes
extras/fotfskills/res/fotfskills/removed_ids.txt, one `block|item old_id new_id` per line. fotfskills adds these as
permanent registry aliases once Tinkers is gone, so slime islands, slime-wood builds and items in chests turn into the
replacement instead of vanishing. Items with no line (parts, casts, ingots, buckets) simply disappear.
"""
import json
import re
import sys
import zipfile
from pathlib import Path

PACK = Path(__file__).resolve().parents[2]
OUT = PACK / 'extras' / 'fotfskills' / 'res' / 'fotfskills' / 'removed_ids.txt'
DEFAULT_LEVEL = PACK.parent / 'server' / 'data' / 'world' / 'level.dat'
DEFAULT_JAR = PACK.parent / 'server' / 'data' / 'mods' / 'TConstruct-1.20.1-3.12.1.231.jar'

WOODS = {'greenheart': 'jungle', 'skyroot': 'birch', 'bloodshroom': 'crimson', 'enderbark': 'mangrove',
         'blazewood': 'crimson', 'nahuatl': 'dark_oak'}
# slime colour -> (leaves, sapling, tall grass, fern)
SLIME = {'earth': ('jungle_leaves', 'jungle_sapling', 'grass', 'fern'),
         'sky': ('azalea_leaves', 'birch_sapling', 'grass', 'fern'),
         'ender': ('mangrove_leaves', 'mangrove_propagule', 'air', 'air'),
         'blood': ('nether_wart_block', 'crimson_fungus', 'crimson_roots', 'crimson_roots'),
         'ichor': ('shroomlight', 'crimson_fungus', 'crimson_roots', 'crimson_roots')}
# slime dirt colour -> (grass, dirt): the ender islands float in the End, the ichor ones in the Nether
DIRT = {'vanilla': ('grass_block', 'dirt'), 'earth': ('grass_block', 'dirt'), 'sky': ('grass_block', 'dirt'),
        'ichor': ('crimson_nylium', 'netherrack'), 'ender': ('end_stone', 'end_stone')}
COLOURS = ['white', 'orange', 'magenta', 'light_blue', 'yellow', 'lime', 'pink', 'gray', 'light_gray', 'cyan',
           'purple', 'blue', 'brown', 'green', 'red', 'black']
HEADS = {'zombified_piglin': 'piglin', 'piglin_brute': 'piglin', 'drowned': 'zombie', 'husk': 'zombie',
         'stray': 'skeleton', 'blaze': 'skeleton', 'enderman': 'skeleton', 'spider': 'skeleton',
         'cave_spider': 'skeleton'}
TOOLS = {'pickaxe': 'iron_pickaxe', 'pickadze': 'iron_pickaxe', 'sledge_hammer': 'iron_pickaxe',
         'vein_hammer': 'iron_pickaxe', 'war_pick': 'iron_pickaxe', 'mattock': 'iron_shovel', 'excavator': 'iron_shovel',
         'hand_axe': 'iron_axe', 'broad_axe': 'iron_axe', 'minotaur_axe': 'iron_axe', 'throwing_axe': 'iron_axe',
         'kama': 'iron_hoe', 'scythe': 'iron_hoe', 'dagger': 'iron_sword', 'sword': 'iron_sword', 'cleaver': 'iron_sword',
         'swasher': 'iron_sword', 'javelin': 'iron_sword', 'longbow': 'bow', 'crossbow': 'crossbow',
         'battlesign': 'shield', 'plate_shield': 'shield', 'travelers_shield': 'shield', 'fishing_rod': 'fishing_rod',
         'flint_and_brick': 'flint_and_steel', 'melting_pan': 'farmersdelight:skillet',
         'plate_helmet': 'iron_helmet', 'plate_chestplate': 'iron_chestplate', 'plate_leggings': 'iron_leggings',
         'plate_boots': 'iron_boots', 'travelers_helmet': 'leather_helmet', 'travelers_chestplate': 'leather_chestplate',
         'travelers_leggings': 'leather_leggings', 'travelers_boots': 'leather_boots', 'slime_helmet': 'leather_helmet',
         'slimy_chestplate': 'leather_chestplate', 'slime_leggings': 'leather_leggings', 'slime_boots': 'leather_boots',
         'bacon': 'cooked_porkchop', 'jeweled_apple': 'golden_apple', 'meat_soup': 'rabbit_stew'}


def wood_block(wood, rest):
    """greenheart_planks_stairs -> jungle_stairs, crimson's log/wood -> stem/hyphae."""
    nether = wood in ('crimson', 'warped')
    rest = {'planks_stairs': 'stairs', 'planks_slab': 'slab'}.get(rest, rest)
    if nether:
        rest = {'log': 'stem', 'wood': 'hyphae'}.get(rest, rest)
    if rest == 'roots':
        return 'mangrove_roots'
    return f'{wood}_{rest}'


def block_target(b):
    m = re.fullmatch(r'(stripped_)?(greenheart|skyroot|bloodshroom|enderbark|blazewood|nahuatl)(?:_(.+))?', b)
    if m:
        wood = WOODS[m.group(2)]
        rest = m.group(3) or 'planks'
        if m.group(2) in ('blazewood', 'nahuatl') and rest in ('stairs', 'slab', 'fence', 'fence_gate'):
            rest = 'planks_' + rest if rest in ('stairs', 'slab') else rest
        if m.group(1):
            return 'stripped_' + wood_block(wood, rest)
        return wood_block(wood, rest)
    m = re.fullmatch(r'(\w+?)_(\w+?)_slime_grass', b)      # <grass colour>_<dirt>_slime_grass
    if m and m.group(2) in DIRT:
        return DIRT[m.group(2)][0]
    m = re.fullmatch(r'(earth|sky|ichor|ender)_slime_dirt', b)
    if m:
        return DIRT[m.group(1)][1]
    m = re.fullmatch(r'(potted_)?(earth|sky|ender|blood|ichor)_slime_(leaves|sapling|tall_grass|fern|vine)', b)
    if m:
        leaves, sapling, grass, fern = SLIME[m.group(2)]
        target = {'leaves': leaves, 'sapling': sapling, 'tall_grass': grass, 'fern': fern, 'vine': 'vine'}[m.group(3)]
        if m.group(1):
            return 'potted_' + target if target in ('jungle_sapling', 'birch_sapling', 'mangrove_propagule',
                                                    'crimson_fungus', 'crimson_roots', 'fern') else 'flower_pot'
        return target
    if re.fullmatch(r'\w+_(enderbark|greenheart|skyroot|bloodshroom)_roots', b):
        return 'muddy_mangrove_roots'
    if re.fullmatch(r'\w+_(congealed_slime|slime)', b):
        return 'slime_block'
    m = re.fullmatch(r'(budding|small|medium|large)?_?\w+?_slime_crystal(_bud|_cluster|_block)?', b)
    if m and 'slime_crystal' in b:
        if b.startswith('budding') or b.endswith('_block'):
            return 'amethyst_block'
        if b.endswith('_cluster'):
            return 'amethyst_cluster'
        return f'{m.group(1)}_amethyst_bud'
    if b.endswith('slime_fluid'):
        return 'water'
    if b.endswith('_fluid'):
        return 'air'
    if b.endswith('_cake'):
        return 'cake'
    if b in ('cobalt_ore',):
        return 'nether_gold_ore'
    m = re.fullmatch(r'(\w+?)_(wall_)?head', b)
    if m:
        mob = HEADS.get(m.group(1), 'skeleton')
        kind = 'skull' if mob == 'skeleton' else 'head'
        return f'{mob}_{"wall_" if m.group(2) else ""}{kind}'
    m = re.fullmatch(r'(\w+)_clear_stained_glass(_pane)?', b)
    if m and m.group(1) in COLOURS:
        return f'{m.group(1)}_stained_glass{m.group(2) or ""}'
    if re.search(r'tinted_glass$', b):
        return 'tinted_glass'
    if b.endswith('glass_pane') or b == 'obsidian_pane':
        return 'glass_pane'
    if b.endswith('glass'):
        return 'glass'
    simple = {
        'seared_stone': 'stone', 'seared_stone_stairs': 'stone_stairs', 'seared_stone_slab': 'stone_slab',
        'seared_cobble': 'cobblestone', 'seared_cobble_stairs': 'cobblestone_stairs',
        'seared_cobble_slab': 'cobblestone_slab', 'seared_cobble_wall': 'cobblestone_wall',
        'seared_paver': 'smooth_stone', 'seared_paver_slab': 'smooth_stone_slab', 'seared_paver_stairs': 'stone_stairs',
        'seared_bricks': 'stone_bricks', 'seared_bricks_stairs': 'stone_brick_stairs',
        'seared_bricks_slab': 'stone_brick_slab', 'seared_bricks_wall': 'stone_brick_wall',
        'seared_cracked_bricks': 'cracked_stone_bricks', 'seared_fancy_bricks': 'chiseled_stone_bricks',
        'seared_triangle_bricks': 'chiseled_stone_bricks', 'seared_ladder': 'ladder', 'scorched_ladder': 'ladder',
        'seared_lantern': 'lantern', 'scorched_lantern': 'soul_lantern', 'seared_lamp': 'redstone_lamp',
        'scorched_lamp': 'redstone_lamp',
        'scorched_stone': 'blackstone', 'polished_scorched_stone': 'polished_blackstone',
        'scorched_bricks': 'polished_blackstone_bricks', 'scorched_bricks_stairs': 'polished_blackstone_brick_stairs',
        'scorched_bricks_slab': 'polished_blackstone_brick_slab', 'scorched_bricks_fence': 'nether_brick_fence',
        'chiseled_scorched_bricks': 'chiseled_polished_blackstone', 'scorched_road': 'polished_blackstone',
        'scorched_road_stairs': 'polished_blackstone_stairs', 'scorched_road_slab': 'polished_blackstone_slab',
        'crafting_station': 'crafting_table', 'part_builder': 'crafting_table', 'tinker_station': 'crafting_table',
        'modifier_worktable': 'crafting_table', 'tinkers_anvil': 'anvil', 'scorched_anvil': 'anvil',
        'tinkers_chest': 'chest', 'part_chest': 'chest', 'cast_chest': 'chest', 'grout': 'gravel',
        'nether_grout': 'soul_sand', 'glow': 'air', 'punji': 'air', 'gold_bars': 'iron_bars', 'cheese_block': 'cake',
    }
    if b in simple:
        return simple[b]
    if b.startswith('scorched') or b.endswith('_proxy_tank') or b == 'foundry_controller':
        return 'polished_blackstone_bricks'
    return 'stone_bricks'                                   # catch-all: smeltery parts, metal blocks, platforms


def item_target(i, blocks):
    if i in TOOLS:
        return TOOLS[i]
    if re.fullmatch(r'\w+_slime_(ball|bottle)', i):
        return 'slime_ball'
    if re.fullmatch(r'\w+_slime_spawn_egg', i) or i == 'terracube_spawn_egg':
        return 'slime_spawn_egg'
    if i.endswith('_slime_grass_seeds'):
        return 'wheat_seeds'
    if i in blocks:
        return block_target(i)
    return None


# Every Compat's short mod names -> mod id
EVERYCOMP = {'af': 'another_furniture', 'hc': 'handcrafted', 'fd': 'farmersdelight', 'faf': 'friendsandfoes',
             'ru': 'regions_unexplored', 'tf': 'twilightforest', 'mcf': 'mcwfences', 'mcw': 'mcwwindows',
             'mcwb': 'mcwbridges', 'sup': 'supplementaries', 'cl': 'candlelight', 'mrc': 'refurbished_furniture'}
SLIME_WOODS = {'greenheart': 'jungle', 'skyroot': 'birch', 'bloodshroom': 'crimson', 'enderbark': 'mangrove',
               'earth_slime': 'jungle', 'sky_slime': 'azalea', 'ender_slime': 'mangrove'}


def everycomp_lines(level):
    """Every Compat blocks made in Tinkers woods -> the owning mod's vanilla-wood version (only ids that exist)."""
    import gzip
    data = gzip.open(level).read()
    ids = set(m.decode() for m in re.findall(rb'[a-z0-9_.-]+:[a-z0-9_/.-]+', data))
    by_path = {}
    for i in ids:
        if not i.startswith('everycomp:'):
            by_path.setdefault(i.split(':', 1)[1], []).append(i)
    lines = []
    for i in sorted(x for x in ids if x.startswith('everycomp:') and '/tconstruct/' in x):
        abbr, _, rest = i.split(':')[1].split('/')
        wood = next((w for w in sorted(SLIME_WOODS, key=len, reverse=True) if w in rest), None)
        if not wood:
            continue
        options = by_path.get(rest.replace(wood, SLIME_WOODS[wood]), [])
        owner = [o for o in options if o.split(':')[0] == EVERYCOMP.get(abbr)]
        target = owner[0] if owner else (options[0] if len(options) == 1 else None)
        if target:
            lines += [f'block {i} {target}', f'item {i} {target}']
    return lines


def main():
    jar = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_JAR
    z = zipfile.ZipFile(jar)
    blocks = sorted({n.split('/')[-1][:-5] for n in z.namelist()
                     if n.startswith('assets/tconstruct/blockstates/') and n.endswith('.json')})
    lang = json.loads(z.read('assets/tconstruct/lang/en_us.json'))
    items = sorted({k.split('.', 2)[2] for k in lang if k.startswith('item.tconstruct.') and k.count('.') == 2}
                   | {k.split('.', 2)[2] for k in lang if k.startswith('block.tconstruct.') and k.count('.') == 2})

    def full(t):
        return t if ':' in t else 'minecraft:' + t

    lines = [f'block tconstruct:{b} {full(block_target(b))}' for b in blocks]
    lines += [f'item tconstruct:{i} {full(t)}' for i in items if (t := item_target(i, set(blocks))) and t != 'air']
    level = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_LEVEL
    extra = everycomp_lines(level) if level.exists() else []
    lines += extra
    OUT.write_text('# old id -> replacement, made by tools/removed/make_tinkers_remap.py\n' + '\n'.join(lines) + '\n',
                   encoding='utf-8')
    print(f'{len(blocks)} blocks, {len(lines) - len(blocks) - len(extra)} items, {len(extra) // 2} Every Compat ids'
          f' -> {OUT.relative_to(PACK)}')


if __name__ == '__main__':
    main()
