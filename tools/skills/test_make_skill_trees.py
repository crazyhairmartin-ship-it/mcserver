import json
import re
from pathlib import Path

import make_skill_trees as g

DATA = json.loads((Path(__file__).parent / 'trees.json').read_text(encoding='utf-8'))
TIERS = DATA['tiers']


def tree(tree_id):
    return next(t for t in DATA['trees'] if t['id'] == tree_id)


def node(tree_id, name):
    return next(n for n in tree(tree_id)['nodes'] if n['name'] == name)


def test_slug_and_unique_ids():
    assert g.slug("Miner's Might") == 'miners_might'
    assert g.slug('Berserker\'s Axe') == 'berserkers_axe'
    assert g.slug('Prospector II') == 'prospector_ii'
    for t in DATA['trees']:
        ids = [i for n in t['nodes'] for i in g.rank_ids(n)]
        assert len(ids) == len(set(ids)), t['id']


def test_rank_chain():
    files = g.build_category(tree('mining'), TIERS)
    skills, uni = files['skills.json'], files['connections.json']['normal']['unidirectional']
    assert [s for s in skills if s.startswith('stone_sense_')] == [f'stone_sense_{k}' for k in range(1, 6)]
    assert skills['stone_sense_1'].get('root') is True
    assert 'root' not in skills['stone_sense_2']
    for k in range(1, 5):
        assert [f'stone_sense_{k}', f'stone_sense_{k + 1}'] in uni


def test_tier_gate_and_titles():
    defs = g.build_category(tree('mining'), TIERS)['definitions.json']
    assert defs['stone_sense_1']['required_spent_points'] == 0
    assert defs['prospector_1']['required_spent_points'] == 5
    assert defs['crusher_1']['required_spent_points'] == 15
    assert 'rewards' not in defs['stone_sense_1']  # preview: no effects (dummy is not a config reward type)


def test_needs_node_not_root_and_linked():
    files = g.build_category(tree('mining'), TIERS)
    assert 'root' not in files['skills.json']['prospector_ii_1']
    assert ['prospector_5', 'prospector_ii_1'] in files['connections.json']['normal']['unidirectional']


def test_choice_tier_exclusive_only_between_branches():
    files = g.build_category(tree('range'), TIERS)
    ex = files['connections.json']['exclusive']['bidirectional']
    assert ['rapid_volley_1', 'heavy_draw_1'] in ex
    assert ['fletchers_luck_1', 'seeker_1'] in ex
    named = {i for pair in ex for i in pair}
    assert 'homing_arrows_1' not in named and 'steady_hands_1' not in named


def test_capstones_cost_three_single_rank():
    defs = g.build_category(tree('craft'), TIERS)['definitions.json']
    for sid in ('masterwork_1', 'endless_workshop_1', 'weaponsmith_1', 'armourer_1'):
        assert defs[sid]['cost'] == 3, sid
    assert 'masterwork_2' not in defs
    assert defs['masterwork_1']['frame']['data']['frame'] == 'challenge'
    assert defs['weaponsmith_1']['frame']['data']['frame'] == 'goal'


def test_layout_one_tile_per_node_and_endpoints_exist():
    for t in DATA['trees']:
        files = g.build_category(t, TIERS)
        skills = files['skills.json']
        tiles = {}
        for n in t['nodes']:
            spots = {(skills[i]['x'], skills[i]['y']) for i in g.rank_ids(n)}
            assert len(spots) == 1, (t['id'], n['name'])    # every rank on the same tile
            tiles[n['name']] = spots.pop()
        assert len(set(tiles.values())) == len(tiles), t['id']  # different nodes never share a tile
        conns = files['connections.json']
        for pair in conns['normal']['unidirectional'] + conns['exclusive']['bidirectional']:
            assert all(p in skills for p in pair), (t['id'], pair)


def test_full_tree_fits_level_cap():
    for t in DATA['trees']:
        total = 0
        for tier in TIERS:
            row = [n for n in t['nodes'] if n['t'] == tier['n']]
            total += sum(n['r'] * n['c'] for n in row if not n['b'])
            total += max([sum(n['r'] * n['c'] for n in row if n['b'] == br) for br in 'AB'] or [0])
        assert total == 50, (t['id'], total)   # every tree fills at exactly the level cap (Dylan, playtest 1)


def test_generator_removes_stale_categories(tmp_path):
    out = tmp_path / 'puffish_skills'
    (out / 'categories' / 'wood').mkdir(parents=True)
    (out / 'categories' / 'wood' / 'skills.json').write_text('{}')
    g.write_config(DATA, out)
    assert not (out / 'categories' / 'wood').exists()
    config = json.loads((out / 'config.json').read_text())
    assert config['version'] == 3 and len(config['categories']) == 12
    assert (out / 'categories' / 'forage' / 'definitions.json').exists()  # Pufferfish reads categories/<id>/


def test_every_node_has_its_own_icon_and_trees_vary():
    for t in DATA['trees']:
        defs = g.build_category(t, TIERS)['definitions.json']
        nodes = [d for sid, d in defs.items() if not sid.startswith('tier_')]
        icons = {d['icon']['data']['item'] for d in nodes}
        assert len(icons) >= 10, (t['id'], len(icons))
        for n in t['nodes']:
            assert g.base_name(n['name']) in g.ICONS[t['id']], (t['id'], n['name'])
    assert g.build_category(tree('mining'), TIERS)['definitions.json']['prospector_ii_1']['icon']['data']['item'] == 'minecraft:raw_iron'


def test_tier_labels_show_points_and_never_unlock():
    files = g.build_category(tree('range'), TIERS)
    defs, skills, conns = files['definitions.json'], files['skills.json'], files['connections.json']
    linked = {i for pair in conns['normal']['unidirectional'] + conns['exclusive']['bidirectional'] for i in pair}
    for tier in TIERS:
        sid = f'tier_{tier["n"]}_label'
        assert sid in skills and 'root' not in skills[sid] and sid not in linked
        assert defs[sid]['title'].startswith(f'Tier {tier["n"]}')
    assert '10 points' in defs['tier_3_label']['title'] and 'Pick one' in defs['tier_3_label']['description']
    assert 'Start' in defs['tier_1_label']['title']


def test_or_marker_sits_between_choice_branches():
    files = g.build_category(tree('range'), TIERS)
    skills = files['skills.json']
    assert files['definitions.json']['tier_3_or']['title'] == 'OR'
    a, o, b = skills['rapid_volley_1']['x'], skills['tier_3_or']['x'], skills['heavy_draw_1']['x']
    assert a < o < b and skills['tier_3_or']['y'] == skills['rapid_volley_1']['y']
    assert 'tier_4_or' not in skills


def test_choice_nodes_name_the_other_branch():
    defs = g.build_category(tree('range'), TIERS)['definitions.json']
    assert 'Pick one: this or Heavy Draw' in defs['rapid_volley_1']['extra_description']
    assert 'Pick one: this or Rapid Volley' in defs['heavy_draw_3']['extra_description']


def test_rank_text_is_that_ranks_effect_and_extras_are_separate():
    defs = g.build_category(tree('mining'), TIERS)['definitions.json']
    assert defs['stone_sense_1']['title'] == 'Stone Sense' and defs['stone_sense_5']['title'] == 'Stone Sense'
    assert defs['stone_sense_1']['description'] == '+4% mining speed'
    assert defs['stone_sense_2']['description'] == '+8% mining speed'
    assert defs['stone_sense_5']['description'] == '+20% mining speed'
    assert defs['miners_might_3']['description'] == '+0.9 damage with pickaxes, hammers and maces'
    assert 'extra_description' not in defs['miners_might_3']   # no 'feeds' text in tooltips
    assert defs['prospector_ii_1']['extra_description'] == 'Needs Prospector (all ranks).'
    assert defs['ore_nose_1']['description'] == '3% chance that stone you mine also drops a raw ore nugget'
    assert 'extra_description' not in defs['ore_nose_1']
    taming = g.build_category(tree('taming'), TIERS)['definitions.json']
    assert taming['gentle_hand_2']['description'] == '20% that a failed taming attempt succeeds anyway'


def test_tier_and_or_tiles_use_numeral_textures():
    defs = g.build_category(tree('range'), TIERS)['definitions.json']
    assert defs['tier_3_label']['icon'] == {'type': 'texture', 'data': {'texture': 'fotfskills:textures/gui/skills/tier_3.png'}}
    assert defs['tier_3_or']['icon'] == {'type': 'texture', 'data': {'texture': 'fotfskills:textures/gui/skills/or.png'}}


def test_rank_text_scales_every_amount_but_not_durations_or_costs():
    assert g.rank_text(node('agility', 'Throwing Arm'), 2) == 'Thrown weapons fly 16% faster and hit 16% harder'
    assert g.rank_text(node('magic', 'Staff Adept'), 3) == 'Holding a staff or wand: +12% spell power and -12% cooldowns'
    assert g.rank_text(node('range', 'Arcane Arrows'), 2) == 'Full-draw shots spend 5 mana for +30% magic damage'
    assert g.rank_text(node('mining', 'Stonehide'), 2) == 'Mining grants +2 armour for 30 s'
    assert g.rank_text(node('agility', 'Long Rope'), 3) == 'Grappling hook reaches 12 blocks further'
    assert g.rank_text(node('farm', 'Grim Harvest'), 3) == 'Scythe kills heal you 3 health'


XP = json.loads((Path(__file__).parent / 'xp.json').read_text(encoding='utf-8'))


def test_every_tree_has_xp_sources_and_the_spec_curve():
    for t in DATA['trees']:
        exp = g.build_category(t, TIERS, xp=XP)['experience.json']
        assert exp['level_limit'] == 50
        assert exp['experience_per_level'] == {'type': 'expression', 'data': {'expression': '30 + 12 * level ^ 1.35'}}
        assert exp['sources'], t['id']
        for s in exp['sources']:
            assert s['type'].startswith(('puffish_skills:', 'fotfskills:')) and 'data' in s


def test_combat_xp_is_from_hits_and_defense_ignores_environment():
    types = {t['id']: [s['type'] for s in g.build_category(t, TIERS, xp=XP)['experience.json']['sources']]
             for t in DATA['trees']}
    assert types['attack'] == ['puffish_skills:deal_damage']
    assert types['range'] == ['puffish_skills:deal_damage']
    assert 'puffish_skills:kill_entity' not in sum(types.values(), [])
    assert set(types['defense']) == {'fotfskills:take_hit', 'fotfskills:shield_block'}   # per-attacker limit, no self/environment damage


def test_no_experience_file_without_xp_data():
    assert 'experience.json' not in g.build_category(tree('mining'), TIERS)


def test_written_config_has_experience_per_category(tmp_path):
    g.write_config(DATA, tmp_path, xp=XP)
    for t in DATA['trees']:
        assert (tmp_path / 'categories' / t['id'] / 'experience.json').exists()


PERKS = json.loads((Path(__file__).parent / 'perks.json').read_text(encoding='utf-8'))


def test_stat_nodes_get_one_attribute_reward_per_rank():
    defs = g.build_category(tree('attack'), TIERS, XP, PERKS)['definitions.json']
    reward = {'type': 'puffish_skills:attribute',
              'data': {'attribute': 'minecraft:generic.attack_damage', 'value': 0.3, 'operation': 'addition'}}
    for k in range(1, 6):
        assert defs[f'sharpened_{k}']['rewards'] == [reward]
    assert defs['momentum_1']['rewards'] == [{'type': 'fotfskills:perk', 'data': {'perk': 'momentum', 'value': 0.05}}]   # a perk, not an attribute
    assert 'rewards' not in defs['tier_1_label']


def test_mana_pool_raises_the_shared_pool():
    defs = g.build_category(tree('magic'), TIERS, XP, PERKS)['definitions.json']
    attrs = {r['data']['attribute'] for r in defs['mana_pool_1']['rewards']}
    assert attrs == {'irons_spellbooks:max_mana'}   # shared mana: one pool, so Mana Pool counts once


PERK_IDS = set(re.findall(r'Map\.entry\("([a-z_]+)"',
                          (Path(__file__).parents[2] / 'extras/fotfskills/src/fotfskills/perk/Perks.java').read_text(encoding='utf-8')))


def test_perks_only_name_real_nodes_and_known_perks():
    assert 'ore_drops' in PERK_IDS
    for tree_id, nodes in PERKS.items():
        slugs = {g.slug(n['name']) for n in tree(tree_id)['nodes']}
        for node_slug, rewards in nodes.items():
            assert node_slug in slugs, (tree_id, node_slug)
            for r in rewards:
                if r['type'] == 'puffish_skills:attribute':
                    assert r['data']['operation'] in {'addition', 'multiply_base', 'multiply_total'}
                else:
                    assert r['type'] == 'fotfskills:perk' and r['data']['perk'] in PERK_IDS, r
                    assert r['data']['value'] > 0


def test_common_perk_nodes_are_wired():
    expect = {('mining', 'prospector_1'): ('ore_drops', 0.03), ('range', 'quiver_care_2'): ('ammo_save', 0.08),
              ('craft', 'endless_workshop_1'): ('craft_free', 0.1), ('fish', 'patient_angler_1'): ('bite_speed', 0.05),
              ('agility', 'featherfall_1'): ('fall_immunity', 15), ('defense', 'unbreakable_1'): ('armour_durability', 0.5)}
    for (tree_id, sid), (perk, value) in expect.items():
        defs = g.build_category(tree(tree_id), TIERS, XP, PERKS)['definitions.json']
        assert {'type': 'fotfskills:perk', 'data': {'perk': perk, 'value': value}} in defs[sid]['rewards'], sid


def test_gathering_xp_uses_the_placed_block_aware_source():
    for tree_id in ('mining', 'forage', 'farm'):
        types = [s['type'] for s in g.build_category(tree(tree_id), TIERS, xp=XP)['experience.json']['sources']]
        assert 'fotfskills:break' in types, tree_id
        assert not {'puffish_skills:mine_block', 'puffish_skills:break_block'} & set(types), tree_id
    farm = g.build_category(tree('farm'), TIERS, xp=XP)['experience.json']['sources']
    rules = next(s for s in farm if s['type'] == 'fotfskills:break')['data']['rules']
    assert rules == [{'mature_crop': True, 'experience': 3}]


def test_weapon_and_conditional_nodes_are_wired():
    expect = {('mining', 'miners_might_2'): ('dmg_pickaxe_blunt', 0.3), ('forage', 'axe_mastery_1'): ('dmg_axe', 0.3),
              ('attack', 'heavy_arms_1'): ('pct_two_handed', 0.1), ('defense', 'second_wind_1'): ('second_wind', 1),
              ('agility', 'throwing_arm_1'): ('thrown_speed', 0.08), ('magic', 'staff_adept_1'): ('staff_cooldown', 0.04),
              ('cook', 'warriors_feast_1'): ('feast_spell', 0.1), ('fish', 'seas_blessing_1'): ('seas_blessing', 1)}
    for (tree_id, sid), (perk, value) in expect.items():
        defs = g.build_category(tree(tree_id), TIERS, XP, PERKS)['definitions.json']
        assert {'type': 'fotfskills:perk', 'data': {'perk': perk, 'value': value}} in defs[sid]['rewards'], sid
    magic = g.build_category(tree('magic'), TIERS, XP, PERKS)['definitions.json']
    assert {'type': 'puffish_skills:attribute', 'data': {'attribute': 'irons_spellbooks:spell_power', 'value': 0.1,
            'operation': 'multiply_base'}} in magic['battlemage_1']['rewards']


def test_pet_and_mount_nodes_are_wired():
    expect = {('taming', 'bonded_3'): ('pet_health', 0.05), ('taming', 'alpha_1'): ('pet_stun', 0.1),
              ('taming', 'breeder_2'): ('twins', 0.06), ('taming', 'gentle_hand_1'): ('gentle_hand', 0.1),
              ('range', 'falconer_1'): ('falconer', 0.05), ('defense', 'guardian_1'): ('guardian', 0.05),
              ('agility', 'rider_1'): ('ride_speed', 0.04), ('craft', 'saddler_1'): ('ride_armor', 2),
              ('cook', 'pet_treats_1'): ('pet_treats', 5), ('magic', 'natures_mend_1'): ('natures_mend', 1)}
    for (tree_id, sid), (perk, value) in expect.items():
        defs = g.build_category(tree(tree_id), TIERS, XP, PERKS)['definitions.json']
        assert {'type': 'fotfskills:perk', 'data': {'perk': perk, 'value': value}} in defs[sid]['rewards'], sid


def test_crafting_cooking_farming_fishing_nodes_are_wired():
    expect = {('mining', 'smelter_1'): ('autosmelt', 0.12), ('farm', 'green_thumb_1'): ('green_thumb', 0.06),
              ('farm', 'sweeping_harvest_2'): ('sweeping_harvest', 1), ('cook', 'hearty_meals_1'): ('hearty_meals', 0.1),
              ('craft', 'enchanted_crafts_1'): ('enchant_level', 1), ('craft', 'masterwork_1'): ('masterwork', 1),
              ('fish', 'sea_legs_1'): ('sea_legs', 0.1), ('forage', 'berry_picker_1'): ('berry_picker', 0.1)}
    for (tree_id, sid), (perk, value) in expect.items():
        defs = g.build_category(tree(tree_id), TIERS, XP, PERKS)['definitions.json']
        assert {'type': 'fotfskills:perk', 'data': {'perk': perk, 'value': value}} in defs[sid]['rewards'], sid
    fish = g.build_category(tree('fish'), TIERS, XP, PERKS)['definitions.json']
    assert {'type': 'puffish_skills:attribute', 'data': {'attribute': 'minecraft:generic.luck', 'value': 1,
            'operation': 'addition'}} in fish['lucky_line_1']['rewards']


def test_range_shield_magic_specials_are_wired():
    expect = {('range', 'homing_arrows_1'): ('homing', 0.05), ('range', 'seeker_1'): ('seeker', 1),
              ('range', 'multishot_1'): ('multishot', 0.1), ('range', 'arcane_arrows_1'): ('arcane_arrows', 0.15),
              ('range', 'retriever_1'): ('retriever', 0.5), ('defense', 'shield_wall_1'): ('shield_wall', 0.15),
              ('defense', 'bulwark_1'): ('bulwark', 0.1), ('magic', 'mana_shield_1'): ('mana_shield', 1),
              ('magic', 'wellspring_1'): ('wellspring', 1), ('forage', 'druids_grove_1'): ('druids_grove', 0.05),
              ('mining', 'earthshaker_1'): ('earthshaker', 1), ('farm', 'reapers_due_1'): ('reapers_due', 1)}
    for (tree_id, sid), (perk, value) in expect.items():
        defs = g.build_category(tree(tree_id), TIERS, XP, PERKS)['definitions.json']
        assert {'type': 'fotfskills:perk', 'data': {'perk': perk, 'value': value}} in defs[sid]['rewards'], sid


def test_scroll_saver_is_removed():
    assert 'Scroll Saver' not in {n['name'] for n in tree('magic')['nodes']}
    assert 'scroll_saver' not in PERKS.get('magic', {})


def test_xp_rates_after_playtest_1():
    src = XP['sources']
    def data(tree_id, kind):
        return next(s['data'] for s in src[tree_id] if s['type'] == kind)
    assert data('fish', 'puffish_skills:fish_item')['experience'] == '25'                    # was too slow
    assert data('agility', 'fotfskills:move')['meters_per_xp'] == 2                          # was way too slow
    assert data('defense', 'fotfskills:take_hit')['per_damage'] == 0.5                       # was way too fast
    assert data('defense', 'fotfskills:shield_block')['per_damage'] == 0.5
    assert 'damage * 0.6' in data('attack', 'puffish_skills:deal_damage')['experience'][0]['expression']   # a bit fast
    assert data('craft', 'fotfskills:craft_gear')['per_item'] == 25                          # was too slow
    assert data('craft', 'fotfskills:craft_any')['per_item'] == 2                            # any real recipe counts
    assert data('taming', 'fotfskills:tame')['experience'] == 75                             # relatively faster


def test_phase4_nodes_are_wired():
    expect = {('agility', 'long_rope_1'): ('hook_range', 4), ('agility', 'long_rope_ii_1'): ('hook_range', 4),
              ('agility', 'hookmaster_1'): ('hook_speed', 0.15), ('agility', 'motor_reel_1'): ('hook_motor', 1),
              ('agility', 'double_jump_1'): ('double_jump', 1), ('taming', 'ferality_1'): ('ferality', 0.15)}
    for (tree_id, sid), (perk, value) in expect.items():
        defs = g.build_category(tree(tree_id), TIERS, XP, PERKS)['definitions.json']
        assert {'type': 'fotfskills:perk', 'data': {'perk': perk, 'value': value}} in defs[sid]['rewards'], sid
    agility = g.build_category(tree('agility'), TIERS, XP, PERKS)['definitions.json']
    assert {'type': 'puffish_skills:attribute', 'data': {'attribute': 'parcool:parcool.max_stamina', 'value': 0.05,
            'operation': 'multiply_base'}} in agility['light_feet_1']['rewards']
    assert agility['second_breath_1']['rewards'][0]['data']['attribute'] == 'parcool:parcool.stamina_recovery'
    assert agility['roll_master_1']['rewards'][0]['data']['attribute'] == 'parcool:parcool.breakfall.damage_reduction'


def test_ferality_spares_pets_and_makes_them_feral():
    node = next(n for n in tree('taming')['nodes'] if n['name'] == 'Ferality')
    assert 'killing blow' in node['d'] and 'Strength II' in node['d']


def test_every_description_has_a_number():
    for t in DATA['trees']:
        for n in t['nodes']:
            assert any(ch.isdigit() for ch in n['d']), (t['id'], n['name'], n['d'])


def test_agility_nodes_unlock_parcool_moves():
    agility = g.build_category(tree('agility'), TIERS, XP, PERKS)['definitions.json']
    for sid, perk in [('freerunner_1', 'pc_freerunner'), ('spring_step_1', 'pc_spring'), ('featherfall_1', 'pc_skydive'),
                      ('double_jump_1', 'pc_trick')]:
        assert {'type': 'fotfskills:perk', 'data': {'perk': perk, 'value': 1}} in agility[sid]['rewards'], sid


def test_magic_rework_tier3_is_spell_power_or_summons():
    names = {n['name']: n for n in tree('magic')['nodes']}
    assert names['Battlemage']['b'] == 'A' and names['Summoner']['b'] == 'B' and names['Summoner']['t'] == 3
    assert names['Sourcecraft']['t'] == 2 and 'Artificer' not in names
