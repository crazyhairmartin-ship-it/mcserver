"""Writes the in-game test kit datapack for the TEST server only (never shipped in the pack).

    python tools/testkit/make_test_datapack.py [world folder, default ../server-test/data/world]

Then run /reload (or restart the test server). In game: /function fotftest:help
"""
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PACK = os.path.normpath(os.path.join(HERE, '..', '..'))
TREES = ['mining', 'forage', 'farm', 'fish', 'cook', 'craft', 'attack', 'range', 'defense', 'agility', 'magic', 'taming']


def enchanted(item, enchants):
    parts = ','.join(f'{{id:"minecraft:{e}",lvl:{lvl}s}}' for e, lvl in enchants)
    return f'{item}{{Enchantments:[{parts}]}}'


KITS = {
    'mining': ['diamond_pickaxe', 'torch 64', 'cooked_beef 32'],
    'forage': ['iron_axe', 'butterflies:butterfly_net', 'shears', 'glass_bottle 8', 'bee_spawn_egg 2', 'beehive'],
    'farm': ['iron_hoe', 'spartanweaponry:iron_scythe', 'wheat_seeds 64', 'farm_and_charm:tomato_seeds 16', 'bone_meal 64',
             'water_bucket', 'dirt 64', 'composter', 'zombie_spawn_egg 6'],
    'fish': ['aquaculture:iron_fishing_rod', 'aquaculture:worm 16', 'aquaculture:leech 16', 'fishing_rod'],
    'cook': ['farmersdelight:cooking_pot', 'farmersdelight:stove', 'farm_and_charm:stove', 'beef 16', 'potato 16',
             'carrot 16', 'farm_and_charm:onion 8', 'bowl 16', 'farmersdelight:roast_chicken_block 2',
             'farmersdelight:apple_pie 2', 'cake 2', 'vinery:red_wine 4', 'brewery:beer_wheat 4',
             'farm_and_charm:strawberry_tea 4', 'coal 32'],
    'craft': ['furnace', 'smoker', 'blast_furnace', 'raw_iron 64', 'coal 64', 'grindstone', 'crafting_table',
              'iron_ingot 64', 'stick 32', 'string 16', 'feather 16', 'flint 16', 'book 8', 'leather 16',
              enchanted('iron_sword', [('sharpness', 2)]) + ' 3', enchanted('iron_chestplate', [('protection', 2)]) + ' 2'],
    'attack': ['iron_sword', 'spartanweaponry:iron_scythe', 'spartanweaponry:iron_greatsword',
               'spartanweaponry:iron_flanged_mace', 'iron_axe', 'spartanweaponry:iron_dagger', 'zombie_spawn_egg 16'],
    'range': ['bow', 'crossbow', 'arrow 192', 'spartanweaponry:iron_javelin 4', 'spartanweaponry:iron_throwing_knife 8',
              'trident', 'zombie_spawn_egg 16', 'skeleton_spawn_egg 4'],
    'defense': ['shield', 'iron_helmet', 'iron_chestplate', 'iron_leggings', 'iron_boots', 'zombie_spawn_egg 16',
                'skeleton_spawn_egg 4', 'creeper_spawn_egg 2'],
    'agility': ['grapplemod:grapplinghook', 'leather_boots', 'ladder 32', 'scaffolding 32'],
    'magic': ['ars_nouveau:novice_spell_book', 'ars_nouveau:glyph_summon_wolves', 'ars_nouveau:glyph_summon_vex',
              'ars_nouveau:glyph_projectile', 'ars_nouveau:glyph_harm', 'ars_nouveau:scribes_table',
              'ars_nouveau:source_gem 32', 'lapis_lazuli 32', 'irons_spellbooks:iron_spell_book',
              'irons_spellbooks:inscription_table', 'zombie_spawn_egg 8'],
    'taming': ['wheat 64', 'carrot 64', 'wheat_seeds 64', 'golden_carrot 32', 'bamboo 32', 'sweet_berries 32',
               'tropical_fish_bucket 8', 'bone 16', 'dandelion 16', 'sheep_spawn_egg 6', 'cow_spawn_egg 2',
               'axolotl_spawn_egg 4', 'goat_spawn_egg 4', 'panda_spawn_egg 4', 'horse_spawn_egg 4',
               'rabbit_spawn_egg 4', 'fox_spawn_egg 4', 'mooshroom_spawn_egg 4', 'wolf_spawn_egg 2',
               'domesticationinnovation:pet_bed_red', 'lead 4', 'saddle 2'],
}
EXTRA = {
    'magic': ['createScroll irons_spellbooks:raise_dead 3', 'createScroll irons_spellbooks:summon_vex 3',
              'createScroll irons_spellbooks:summon_polar_bear 3', 'createScroll irons_spellbooks:firebolt 3'],
    'mining': ['effect give @s night_vision 1800 0 true'],
}


def give(entry):
    item, _, count = entry.partition(' ')
    if ':' not in item.split('{')[0]:
        item = 'minecraft:' + item
    return f'give @s {item} {count or 1}'


def skill_ids(tree):
    skills = json.load(open(os.path.join(PACK, 'config', 'puffish_skills', 'categories', tree, 'skills.json'), encoding='utf-8'))
    return [sid for sid in skills if not sid.startswith('tier_')]


def tell(text, color='yellow'):
    return 'tellraw @s ' + json.dumps({'text': text, 'color': color})


def functions():
    out = {}
    for tree in TREES:
        out[f'tree/{tree}'] = [f'puffish_skills skills unlock @s {tree} {sid}' for sid in skill_ids(tree)] + [
            tell(f'Unlocked every {tree} node (both branches). /function fotftest:reset/{tree} to take them back.')]
        out[f'reset/{tree}'] = [f'puffish_skills skills reset @s {tree}', tell(f'{tree} nodes reset.')]
        out[f'kit/{tree}'] = [give(e) for e in KITS[tree]] + EXTRA.get(tree, []) + [tell(f'{tree} test kit given.')]
    out['all'] = [f'function fotftest:tree/{t}' for t in TREES]
    out['reset/all'] = [f'function fotftest:reset/{t}' for t in TREES]
    out['start'] = ['gamemode survival @s', 'effect clear @s', 'effect give @s instant_health 1 10 true',
                    'effect give @s saturation 1 20 true', 'time set day', 'weather clear', 'xp add @s 100 levels',
                    tell('Survival, healed, fed, daytime, +100 XP levels. Perks behave differently in creative.')]
    out['clear'] = ['kill @e[type=!player,type=!item_frame,type=!armor_stand,distance=..40,tag=!keep]',
                    tell('Cleared mobs and items within 40 blocks.')]
    out['merge'] = [give('farmersdelight:tomato 4'), give('farmersdelight:onion 4'), give('farmersdelight:bacon 2'),
                    give('alexsmobs:raw_catfish 2'), 'setblock ~2 ~ ~ farmersdelight:wild_tomatoes',
                    'setblock ~2 ~ ~1 farmersdelight:wild_onions',
                    'setblock ~-2 ~ ~ chest{Items:[{Slot:0b,id:"farmersdelight:tomato_seeds",Count:8b},'
                    '{Slot:1b,id:"wildernature:venison",Count:4b},{Slot:2b,id:"wildernature:fish_oil",Count:4b}]}',
                    tell('Farming merge: the items you just got should already be Farm & Charm / kept versions. '
                         'Break the wild crops (east) and empty the chest (west): tomato seeds, venison and fish oil should convert.')]
    out['help'] = [tell('FOTF test kit', 'gold'),
                   tell('/function fotftest:start  - survival, heal, daytime, +100 XP levels'),
                   tell('/function fotftest:tree/<tree>  - unlock every node in a tree (both branches)'),
                   tell('/function fotftest:reset/<tree>  - lock them again (also reset/all, all)'),
                   tell('/function fotftest:kit/<tree>  - the items that tree\'s tests need'),
                   tell('/function fotftest:merge  - farming merge and drop conversion test'),
                   tell('/function fotftest:clear  - remove mobs and items nearby'),
                   tell('Trees: ' + ' '.join(TREES), 'gray')]
    return out


def main():
    world = sys.argv[1] if len(sys.argv) > 1 else os.path.join(PACK, '..', 'server-test', 'data', 'world')
    root = os.path.join(world, 'datapacks', 'fotftest')
    shutil.rmtree(root, ignore_errors=True)
    os.makedirs(root)
    json.dump({'pack': {'pack_format': 15, 'description': 'FOTF test kit (test server only)'}},
              open(os.path.join(root, 'pack.mcmeta'), 'w'))
    for name, lines in functions().items():
        path = os.path.join(root, 'data', 'fotftest', 'functions', name + '.mcfunction')
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8', newline='\n') as f:
            f.write('\n'.join(lines) + '\n')
    print(f'wrote {len(functions())} functions to {root}')


if __name__ == '__main__':
    main()
