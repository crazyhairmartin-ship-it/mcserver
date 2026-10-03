import json
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
        assert 40 <= total <= 50, (t['id'], total)


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
    assert 'Pick one: this or Heavy Draw' in defs['rapid_volley_1']['description']
    assert 'Pick one: this or Rapid Volley' in defs['heavy_draw_3']['description']


def test_rank_titles_and_now_next_text():
    defs = g.build_category(tree('mining'), TIERS)['definitions.json']
    assert defs['stone_sense_1']['title'] == 'Stone Sense (1/5)'
    assert defs['stone_sense_2']['description'].startswith('Now: +4% mining speed. Next: +8% mining speed.')
    assert defs['stone_sense_1']['description'].startswith('Now: nothing yet. Next: +4% mining speed.')
    assert defs['stone_sense_5']['description'].startswith('Now: +16% mining speed. Next: +20% mining speed (max).')
    assert defs['ore_nose_1']['title'] == 'Ore Nose'
    assert defs['ore_nose_1']['description'].startswith('Plain stone sometimes drops raw nuggets')
    # text without a per-rank number still says which rank it is
    taming = g.build_category(tree('taming'), TIERS)['definitions.json']
    assert taming['gentle_hand_2']['description'].startswith('Rank 2/3: Better odds')


def test_tier_and_or_tiles_use_numeral_textures():
    defs = g.build_category(tree('range'), TIERS)['definitions.json']
    assert defs['tier_3_label']['icon'] == {'type': 'texture', 'data': {'texture': 'fotfskills:textures/gui/skills/tier_3.png'}}
    assert defs['tier_3_or']['icon'] == {'type': 'texture', 'data': {'texture': 'fotfskills:textures/gui/skills/or.png'}}
