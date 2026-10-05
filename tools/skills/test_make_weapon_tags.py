import csv
from pathlib import Path

import make_weapon_tags as w

ROWS = list(csv.DictReader((Path(__file__).parents[2] / 'docs/superpowers/specs/2026-10-03-weapons.csv').open(encoding='utf-8')))


def test_every_type_gets_a_tag_and_tool_is_not_one():
    tags = w.build(ROWS)
    assert set(tags) == set(w.TYPES)
    assert 'tool' not in tags
    for t, tag in tags.items():
        assert tag['replace'] is False and tag['values'], t


def test_items_are_optional_and_unique_and_vanilla_tags_included():
    tags = w.build(ROWS)
    sword = tags['sword']['values']
    ids = [v['id'] for v in sword if isinstance(v, dict)]
    assert len(ids) == len(set(ids))
    assert all(v['required'] is False for v in sword if isinstance(v, dict))
    assert '#minecraft:axes' in tags['axe']['values'] and '#minecraft:hoes' in tags['scythe']['values']
    # swords are listed one by one (no #minecraft:swords) so an item taken off the sword list really leaves it
    assert '#minecraft:swords' not in sword and 'minecraft:iron_sword' in ids
    assert 'irons_spellbooks:twilight_gale' not in ids


def test_multi_type_rows_land_in_each_type_and_firearms_are_crossbows():
    tags = w.build(ROWS)
    def has(t, item):
        return any(isinstance(v, dict) and v['id'] == item for v in tags[t]['values'])
    halberd = next(r['item'] for r in ROWS if r['weapon types'] == 'polearm axe two_handed')
    assert has('polearm', halberd) and has('axe', halberd) and has('two_handed', halberd)
    assert has('crossbow', 'wildernature:blunderbuss')
