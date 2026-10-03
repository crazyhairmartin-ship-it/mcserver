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
