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
    assert defs['stone_sense_3']['title'] == 'Stone Sense III'
    assert defs['ore_nose_1']['title'] == 'Ore Nose'
    assert defs['stone_sense_1']['rewards'] == [{'type': 'puffish_skills:dummy', 'data': {}}]


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


def test_layout_no_overlap_and_endpoints_exist():
    for t in DATA['trees']:
        files = g.build_category(t, TIERS)
        skills = files['skills.json']
        spots = [(s['x'], s['y']) for s in skills.values()]
        assert len(spots) == len(set(spots)), t['id']
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
    (out / 'wood').mkdir(parents=True)
    (out / 'wood' / 'skills.json').write_text('{}')
    g.write_config(DATA, out)
    assert not (out / 'wood').exists()
    config = json.loads((out / 'config.json').read_text())
    assert config['version'] == 3 and len(config['categories']) == 12
    assert (out / 'forage' / 'definitions.json').exists()
