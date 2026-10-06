"""Generate the Friends of the Forest Cookbook, a Patchouli book of every food, sorted by cooking station.

    python tools/cookbook/make_cookbook.py [mods folder]

Reads tools/cookbook/food_dump.json (every edible item with its hunger, saturation and effects, and every recipe that
makes one; dumped from the live server with a temporary KubeJS command) and writes pack/patchouli_books/fotf_cookbook.
Hidden items (trimmed, or the losing copy of a duplicate group) and slices or other partial foods are left out. Each food
is one entry in the chapter of its main station, with its stats and every recipe for it.
"""
import json
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACK = HERE.parents[1]
sys.path.insert(0, str(PACK / 'tools' / 'skills'))
from make_weapon_review import names as lang_names  # noqa: E402

BOOK = PACK / 'patchouli_books' / 'fotf_cookbook'

# station chapter: (title, icon, recipe types), in book order
STATIONS = [
    ('crafting', 'Crafting Table', 'minecraft:crafting_table', ['minecraft:crafting_shaped', 'minecraft:crafting_shapeless']),
    ('fire', 'Furnace, Smoker & Campfire', 'minecraft:smoker',
     ['minecraft:smelting', 'minecraft:smoking', 'minecraft:campfire_cooking']),
    ('cutting', 'Cutting Board', 'farmersdelight:cutting_board', ['farmersdelight:cutting']),
    ('fd_pot', 'Cooking Pot (Farmer\'s Delight)', 'farmersdelight:cooking_pot', ['farmersdelight:cooking']),
    ('stove', 'Stove', 'farm_and_charm:stove', ['farm_and_charm:stove']),
    ('fc_pot', 'Cooking Pot (Farm & Charm)', 'farm_and_charm:cooking_pot', ['farm_and_charm:pot_cooking']),
    ('roaster', 'Roaster', 'farm_and_charm:roaster', ['farm_and_charm:roaster']),
    ('bowl', 'Mixing Bowl', 'farm_and_charm:crafting_bowl', ['farm_and_charm:crafting_bowl']),
    ('mincer', 'Mincer', 'farm_and_charm:mincer', ['farm_and_charm:mincer']),
    ('meadow', 'Cooking Cauldron', 'meadow:cooking_cauldron', ['meadow:cooking']),
    ('baking', 'Baking Station', 'bakery:baker_station', ['bakery:baking_station']),
    ('drinks', 'Brewing & Fermenting', 'vinery:fermentation_barrel',
     ['vinery:wine_fermentation', 'vinery:apple_fermenting', 'vinery:apple_mashing', 'brewery:brewing',
      'herbalbrews:kettle_brewing']),
    ('other', 'Palm Bar (Cocktails)', 'beachparty:palm_bar', ['beachparty:palm_bar_mixing']),
]
SKIP_TYPES = {'tconstruct:casting_table', 'lilis_lucky_lures:fish_trap', 'cataclysm:amethyst_bless'}  # bait and rituals, not cooking
# a food's chapter is its first station in this order (real cooking before the crafting table)
PRIORITY = ['fd_pot', 'fc_pot', 'stove', 'roaster', 'meadow', 'baking', 'bowl', 'mincer', 'drinks', 'fire', 'cutting',
            'other', 'crafting']
GATHERED = ('gathered', 'Grown, Caught & Hunted', 'minecraft:apple')
PARTIAL = re.compile(r'(slice|piece|wedge|portion|_bite|half_|_half|chunk_of)')
# edible building blocks and tools (Alex's Caves candy blocks, the sharpened candy cane) aren't meals
NOT_FOOD = re.compile(r'(_block$|^block_of|_pole$|_pile$|_vine$|^sharpened_|_bricks?$|_stairs$|_slab$)')


def kubejs_list(path, var):
    text = (PACK / 'kubejs' / 'startup_scripts' / path).read_text(encoding='utf-8')
    return text


def hidden_and_renames():
    """Trimmed items are hidden; in a duplicate group the first item is kept and the rest point at it."""
    hidden = set(re.findall(r"'([a-z0-9_]+:[a-z0-9_/]+)'", kubejs_list('trimmed_items.js', 'TRIMMED_ITEMS')))
    keep = {}
    for group in re.findall(r"items:\s*\[([^\]]*)\]", kubejs_list('duplicate_groups.js', 'DUPLICATE_GROUPS')):
        items = re.findall(r"'([a-z0-9_]+:[a-z0-9_/]+)'", group)
        for loser in items[1:]:
            hidden.add(loser)
            keep[loser] = items[0]
    return hidden, keep


def title_case(path):
    return path.replace('_', ' ').title()


def fmt_effect(e):
    name = title_case(e['effect'].split(':')[-1])
    roman = ['', ' II', ' III', ' IV', ' V'][min(max(e['level'], 1), 5) - 1]
    secs = e['seconds']
    time = f'{secs // 60}:{secs % 60:02d}' if secs >= 60 else f'{secs}s'
    chance = '' if e['chance'] >= 1 else f', {round(e["chance"] * 100)}% chance'
    return f'{name}{roman} ({time}{chance})'


def stats_text(food):
    hunger = food['hunger']
    sat = round(hunger * food['saturation'] * 2, 1)
    lines = [f'$(l)Hunger:$() {hunger} ({hunger / 2:g} drumsticks)', f'$(l)Saturation:$() {sat:g}']
    if food['effects']:
        lines.append('$(l)Effects:$() ' + ', '.join(fmt_effect(e) for e in food['effects']))
    extra = [w for w, on in (('Can always eat', food['always']), ('Quick to eat', food['fast'])) if on]
    if extra:
        lines.append(', '.join(extra))
    return '$(br)'.join(lines)


def main():
    mods = sys.argv[1] if len(sys.argv) > 1 else str(PACK.parent / 'server' / 'data' / 'mods')
    dump = json.loads((HERE / 'food_dump.json').read_text(encoding='utf-8'))
    names = lang_names(mods)
    hidden, keep = hidden_and_renames()

    def name(item):
        item = keep.get(item, item)
        return names.get(item, title_case(item.split(':')[1]))

    foods = {i: f for i, f in dump['foods'].items() if i not in hidden and not PARTIAL.search(i.split(':')[1])
             and not NOT_FOOD.search(i.split(':')[1])}
    station_of = {t: s for s, _, _, types in STATIONS for t in types}
    by_food = {}
    for r in dump['recipes']:
        if r['type'] in SKIP_TYPES or r['out'] not in foods or r['type'] not in station_of or not r['ingredients']:
            continue
        if r['type'].startswith('minecraft:crafting') and len(r['ingredients']) == 1 and r['count'] > 1:
            continue                                    # unpacking a crate, bag or storage block isn't cooking
        by_food.setdefault(r['out'], []).append(r)

    if BOOK.exists():                                   # clear old pages (files only: a folder can be held open)
        for old in BOOK.rglob('*.json'):
            old.unlink()
    (BOOK / 'en_us' / 'categories').mkdir(parents=True, exist_ok=True)
    (BOOK / 'book.json').write_text(json.dumps({
        "name": "Friends of the Forest Cookbook",
        "landing_text": "Every food in the forest, sorted by where you cook it.$(br2)Each entry shows how filling the food is, "
                        "any effects it gives, and its recipes. JEI ($(l)R$() on an item) shows the same recipes too.",
        "version": 1, "model": "patchouli:book_brown", "book_texture": "patchouli:textures/gui/book_brown.png",
        "show_progress": False, "use_resource_pack": False, "creative_tab": "minecraft:food_and_drink", "i18n": False,
    }, indent=2) + '\n', encoding='utf-8')

    chapters = {s: [] for s, _, _, _ in STATIONS}
    chapters['gathered'] = []
    for item in foods:
        recipes = by_food.get(item, [])
        stations = {station_of[r['type']] for r in recipes}
        chapter = next((s for s in PRIORITY if s in stations), None)
        if chapter:                                     # foods with no recipe (raw, found) aren't in the book
            chapters[chapter].append(item)

    titles = {s: (t, icon) for s, t, icon, _ in STATIONS}
    titles['gathered'] = GATHERED[1:]
    order = [s for s, _, _, _ in STATIONS] + ['gathered']
    written = 0
    for sortnum, chapter in enumerate(order):
        items = sorted(chapters[chapter], key=name)
        if not items:
            continue
        title, icon = titles[chapter]
        desc = (f'{len(items)} foods you make here.' if chapter != 'gathered'
                else f'{len(items)} foods with no recipe: grow, gather, fish, hunt or find them.')
        (BOOK / 'en_us' / 'categories' / f'{chapter}.json').write_text(json.dumps(
            {"name": title, "description": desc, "icon": icon, "sortnum": sortnum}, indent=2) + '\n', encoding='utf-8')
        edir = BOOK / 'en_us' / 'entries' / chapter
        edir.mkdir(parents=True, exist_ok=True)
        for n, item in enumerate(items):
            pages = [{"type": "patchouli:spotlight", "item": item, "text": stats_text(foods[item])}]
            for r in by_food.get(item, []):
                station = titles[station_of[r['type']]][0]
                if r['type'].startswith('minecraft:crafting'):
                    pages.append({"type": "patchouli:crafting", "recipe": r['id'], "text": f"Makes {r['count']}."})
                    continue
                counts = {}
                for options in r['ingredients']:
                    opts = [o for o in dict.fromkeys(keep.get(o, o) for o in options) if o not in hidden]
                    if not opts:
                        continue
                    label = ' or '.join(name(o) for o in opts[:3]) + (' (or similar)' if len(opts) > 3 else '')
                    counts[label] = counts.get(label, 0) + 1
                lines = [f'$(li){c}x {label}' if c > 1 else f'$(li){label}' for label, c in counts.items()]
                makes = f' (makes {r["count"]})' if r['count'] > 1 else ''
                pages.append({"type": "patchouli:text", "title": station,
                              "text": (f'Makes {r["count"]}.$(br)' if r['count'] > 1 else '') + ''.join(lines)})
            entry = {"name": name(item), "icon": item, "category": f"patchouli:{chapter}", "sortnum": n, "pages": pages}
            fname = re.sub(r'[^a-z0-9_]', '_', item.replace(':', '__'))
            (edir / f'{fname}.json').write_text(json.dumps(entry, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
            written += 1
    print(f'cookbook: {written} foods in {sum(1 for c in order if chapters[c])} chapters')
    for c in order:
        print(f'  {titles[c][0]}: {len(chapters[c])}')


if __name__ == '__main__':
    main()
