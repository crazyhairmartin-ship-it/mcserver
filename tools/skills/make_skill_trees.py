"""Turns tools/skills/trees.json into Pufferfish's Skills config (config/puffish_skills/).

Phase 1 (preview): every node uses the dummy reward. Run: python tools/skills/make_skill_trees.py
"""
import json
import re
import shutil
from pathlib import Path

HERE = Path(__file__).parent
PACK = HERE.parent.parent
OUT = PACK / 'config' / 'puffish_skills'
ROMAN = ['', 'I', 'II', 'III', 'IV', 'V']
ROW_HEIGHT = 56     # pixels between tier rows in the skill screen
RANK_STEP = 26      # pixels between ranks of one node
NODE_GAP = 22       # extra pixels between nodes in a row


def slug(name):
    return re.sub(r'_+', '_', re.sub(r'[^a-z0-9]+', '_', name.lower().replace("'", ''))).strip('_')


def rank_ids(node):
    return [f'{slug(node["name"])}_{k}' for k in range(1, node['r'] + 1)]


def frame(node):
    kind = 'challenge' if node['cap'] else 'goal' if node['b'] else 'task'
    return {'type': 'advancement', 'data': {'frame': kind}}


def description(node, tree):
    text = node['d']
    if node['syn']:
        text += f' (feeds {node["syn"]})'
    if node['needs']:
        text += f' Needs {node["needs"]} (all ranks).'
    return text


def build_category(tree, tiers):
    req = {t['n']: t['req'] for t in tiers}
    by_name = {n['name']: n for n in tree['nodes']}
    definitions, skills = {}, {}
    uni, exclusive = [], []
    rows = {}
    for n in tree['nodes']:
        rows.setdefault(n['t'], []).append(n)
    for tier_n, row in rows.items():
        widths = [n['r'] * RANK_STEP + NODE_GAP for n in row]
        x = -sum(widths) // 2
        for n, w in zip(row, widths):
            ids = rank_ids(n)
            for k, sid in enumerate(ids, start=1):
                definitions[sid] = {
                    'title': n['name'] + (f' {ROMAN[k]}' if n['r'] > 1 else ''),
                    'description': description(n, tree),
                    'icon': {'type': 'item', 'data': {'item': tree['icon']}},
                    'frame': frame(n),
                    'rewards': [{'type': 'puffish_skills:dummy', 'data': {}}],
                    'cost': n['c'],
                    'required_spent_points': req[n['t']],
                }
                skills[sid] = {'x': x + (k - 1) * RANK_STEP, 'y': (tier_n - 1) * ROW_HEIGHT, 'definition': sid}
                if k == 1 and not n['needs']:
                    skills[sid]['root'] = True
                if k > 1:
                    uni.append([ids[k - 2], sid])
            x += w
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
