"""Turns tools/skills/trees.json into Pufferfish's Skills config (config/puffish_skills/).

Phase 1 (preview): nodes have no rewards (no effects). Run: python tools/skills/make_skill_trees.py

Layout: one tile per node. A node's ranks are separate Pufferfish skills stacked on the same tile and chained
(rank 2 needs rank 1); the fotfmail add-on draws a stack as one tile with an "n/total" counter. Each tier row
starts with a label tile ("Tier 3 · 10 points") and choice tiers get an "OR" tile between the two branches.
Label and OR tiles are skills with no connections, so they can never be unlocked.
"""
import json
import re
import shutil
from pathlib import Path

HERE = Path(__file__).parent
PACK = HERE.parent.parent
OUT = PACK / 'config' / 'puffish_skills'
ICONS = json.loads((HERE / 'icons.json').read_text(encoding='utf-8'))
TILE = 30           # pixels between tiles in a row
ROW_HEIGHT = 40     # pixels between tier rows
LABEL_ICON = 'minecraft:oak_sign'
OR_ICON = 'minecraft:lever'
PER_RANK = re.compile(r'^(?P<lead>.*?)(?P<sign>[+-]?)(?P<num>\d+(?:\.\d+)?)(?P<unit>%?)(?P<rest>.*?) per rank(?P<tail>.*)$')


def slug(name):
    return re.sub(r'_+', '_', re.sub(r'[^a-z0-9]+', '_', name.lower().replace("'", ''))).strip('_')


def base_name(name):
    """Icon key: 'Prospector II' shares Prospector's icon."""
    return re.sub(r' II$', '', name)


def rank_ids(node):
    return [f'{slug(node["name"])}_{k}' for k in range(1, node['r'] + 1)]


def frame(node):
    kind = 'challenge' if node['cap'] else 'goal' if node['b'] else 'task'
    return {'type': 'advancement', 'data': {'frame': kind}}


def fmt(value):
    return f'{value:.2f}'.rstrip('0').rstrip('.')


def effect_at(match, amount):
    m = match
    return f'{m["lead"]}{m["sign"]}{fmt(amount)}{m["unit"]}{m["rest"]}{m["tail"]}'.strip()


def rank_text(node, k):
    """What rank k's tooltip says: what you have with k-1 ranks, and what rank k adds."""
    if node['r'] == 1:
        return node['d']
    m = PER_RANK.match(node['d'])
    if not m:
        return f'Rank {k}/{node["r"]}: {node["d"]}'
    step = float(m['num'])
    now = 'nothing yet' if k == 1 else effect_at(m, step * (k - 1))
    nxt = effect_at(m, step * k) + (' (max)' if k == node['r'] else '')
    return f'Now: {now}. Next: {nxt}.'


def description(node, k, tree):
    text = rank_text(node, k)
    if node['b']:
        others = [o['name'] for o in tree['nodes'] if o['t'] == node['t'] and o['b'] and o['b'] != node['b']]
        text += f' Pick one: this or {" / ".join(others)}.'
    if node['syn']:
        text += f' (feeds {node["syn"]})'
    if node['needs']:
        text += f' Needs {node["needs"]} (all ranks).'
    return text


def marker(title, text, icon, req):
    return {'title': title, 'description': text, 'icon': {'type': 'item', 'data': {'item': icon}},
            'frame': {'type': 'advancement', 'data': {'frame': 'task'}}, 'required_spent_points': req}


def build_category(tree, tiers):
    req = {t['n']: t['req'] for t in tiers}
    by_name = {n['name']: n for n in tree['nodes']}
    icons = ICONS[tree['id']]
    definitions, skills = {}, {}
    uni, exclusive = [], []
    rows = {}
    for n in tree['nodes']:
        rows.setdefault(n['t'], []).append(n)
    for tier_n, row in rows.items():
        choice = any(n['b'] for n in row)
        # tiles in this row: label, then nodes, with an OR tile before the first B-branch node
        tiles = [('label', None)]
        for n in row:
            if n['b'] == 'B' and ('or', None) not in tiles:
                tiles.append(('or', None))
            tiles.append(('node', n))
        x0 = -(len(tiles) - 1) * TILE // 2
        y = (tier_n - 1) * ROW_HEIGHT
        for i, (kind, n) in enumerate(tiles):
            x = x0 + i * TILE
            if kind == 'label':
                sid = f'tier_{tier_n}_label'
                points = 'Start' if req[tier_n] == 0 else f'{req[tier_n]} points'
                text = ('Open from the start.' if req[tier_n] == 0 else
                        f'Opens once you have spent {req[tier_n]} points in this tree.')
                if choice:
                    text += ' Pick one branch: taking one locks the other.'
                definitions[sid] = marker(f'Tier {tier_n} · {points}', text, LABEL_ICON, req[tier_n])
                skills[sid] = {'x': x, 'y': y, 'definition': sid}
                continue
            if kind == 'or':
                sid = f'tier_{tier_n}_or'
                definitions[sid] = marker('OR', 'Pick one of the two branches beside this; taking one locks the other.',
                                          OR_ICON, req[tier_n])
                skills[sid] = {'x': x, 'y': y, 'definition': sid}
                continue
            ids = rank_ids(n)
            for k, sid in enumerate(ids, start=1):
                definitions[sid] = {
                    'title': n['name'] + (f' ({k}/{n["r"]})' if n['r'] > 1 else ''),
                    'description': description(n, k, tree),
                    'icon': {'type': 'item', 'data': {'item': icons.get(base_name(n['name']), tree['icon'])}},
                    'frame': frame(n),
                    'cost': n['c'],
                    'required_spent_points': req[n['t']],
                }
                skills[sid] = {'x': x, 'y': y, 'definition': sid}
                if k == 1 and not n['needs']:
                    skills[sid]['root'] = True
                if k > 1:
                    uni.append([ids[k - 2], sid])
    for n in tree['nodes']:
        if n['needs']:
            uni.append([rank_ids(by_name[n['needs']])[-1], rank_ids(n)[0]])
    for tier_n, row in rows.items():
        a = [rank_ids(n)[0] for n in row if n['b'] == 'A']
        b = [rank_ids(n)[0] for n in row if n['b'] == 'B']
        exclusive += [[x, y] for x in a for y in b]
    category = {
        'title': tree['name'],
        'description': f'Earns XP from: {tree["xp"]}',
        'icon': {'type': 'item', 'data': {'item': tree['icon']}},
        'background': tree['background'],
        'unlocked_by_default': True,
        'exclusive_root': False,
        'starting_points': 0,
    }
    connections = {'normal': {'unidirectional': uni}, 'exclusive': {'bidirectional': exclusive}}
    return {'category.json': category, 'definitions.json': definitions, 'skills.json': skills,
            'connections.json': connections}


def write_config(data, out_dir):
    out_dir = Path(out_dir)
    if out_dir.exists():
        shutil.rmtree(out_dir)          # drop stale categories (e.g. a renamed tree)
    out_dir.mkdir(parents=True)
    ids = []
    for tree in data['trees']:
        ids.append(tree['id'])
        cat_dir = out_dir / 'categories' / tree['id']      # Pufferfish reads config/puffish_skills/categories/<id>/
        cat_dir.mkdir(parents=True)
        for name, content in build_category(tree, data['tiers']).items():
            (cat_dir / name).write_text(json.dumps(content, indent=2) + '\n', encoding='utf-8')
    config = {'version': 3, 'show_warnings': True, 'categories': ids}
    (out_dir / 'config.json').write_text(json.dumps(config, indent=2) + '\n', encoding='utf-8')


def main():
    data = json.loads((HERE / 'trees.json').read_text(encoding='utf-8'))
    write_config(data, OUT)
    print(f'wrote {len(data["trees"])} categories to {OUT}')


if __name__ == '__main__':
    main()
