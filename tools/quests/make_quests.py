"""Builds the pack's FTB Quests book from the JSON sources in tools/quests/src.

    python tools/quests/make_quests.py          check everything and write the files
    python tools/quests/make_quests.py --check  check only, write nothing

Writes (and owns: anything else in these places is deleted):
  config/ftbquests/quests/                      data.snbt, chapter_groups.snbt, chapters/*.snbt, reward_tables/*.snbt
  kubejs/startup_scripts/quest_items.generated.js   quest items (letters, notes...) that start quests
  kubejs/server_scripts/quest_givers.generated.js   who gives which quest: villagers, mobs, drops, items

The source format is described in tools/quests/README.md. Every id FTB Quests needs is derived from the source
names (chapter, quest, task number), so regenerating keeps everyone's progress as long as names stay the same.
Ids of items, mobs, biomes, structures, advancements and dimensions are checked against tools/quests/registry.json
(rebuild it with make_registry.py after changing mods).
"""
import difflib
import hashlib
import json
import os
import re
import shutil
import sys

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
SRC = os.path.join(ROOT, 'tools', 'quests', 'src')
OUT = os.path.join(ROOT, 'config', 'ftbquests', 'quests')
ITEMS_JS = os.path.join(ROOT, 'kubejs', 'startup_scripts', 'quest_items.generated.js')
GIVERS_JS = os.path.join(ROOT, 'kubejs', 'server_scripts', 'quest_givers.generated.js')
NAME = re.compile(r'^[a-z0-9_]+$')
SINGULAR = {'items': 'item', 'entities': 'mob', 'biomes': 'biome', 'structures': 'structure',
            'advancements': 'advancement', 'dimensions': 'dimension'}
SHAPES = {'circle', 'square', 'rsquare', 'diamond', 'pentagon', 'hexagon', 'octagon', 'heart', 'gear'}


# ---- SNBT ----

class D(float):
    """A double (written 1.0d)."""


class L(int):
    """A long (written 4L)."""


def snbt(value, indent=0):
    tab = '\t'
    if isinstance(value, bool):
        return 'true' if value else 'false'
    if isinstance(value, D):
        return f'{float(value)!r}d'
    if isinstance(value, L):
        return f'{int(value)}L'
    if isinstance(value, (int, float)):
        return repr(value)
    if isinstance(value, str):
        return '"' + value.replace('\\', '\\\\').replace('"', '\\"') + '"'
    if isinstance(value, list):
        if not value:
            return '[ ]'
        if all(not isinstance(v, (dict, list)) for v in value):
            if len(value) == 1:
                return '[' + snbt(value[0]) + ']'
            inner = ''.join(tab * (indent + 1) + snbt(v) + '\n' for v in value)
            return '[\n' + inner + tab * indent + ']'
        inner = ''.join(tab * (indent + 1) + snbt(v, indent + 1) + '\n' for v in value)
        return '[\n' + inner + tab * indent + ']'
    if isinstance(value, dict):
        lines = [tab * (indent + 1) + k + ': ' + snbt(value[k], indent + 1) + '\n' for k in sorted(value)]
        return '{\n' + ''.join(lines) + tab * indent + '}'
    raise TypeError(f'cannot write {value!r}')


def fid(*parts):
    """A stable FTB Quests id: 16 hex digits, top bit clear so it's a positive long."""
    h = hashlib.sha1('/'.join(parts).encode()).hexdigest()[:16]
    return '%016X' % (int(h, 16) & 0x7FFFFFFFFFFFFFFF or 1)


# ---- checking ----

class Problems:
    def __init__(self):
        self.errors = []
        self.warnings = []

    def error(self, where, msg):
        self.errors.append(f'{where}: {msg}')

    def warn(self, where, msg):
        self.warnings.append(f'{where}: {msg}')


def load_json(path, problems):
    try:
        with open(path, encoding='utf-8') as fh:
            return json.load(fh)
    except ValueError as e:
        problems.error(os.path.relpath(path, ROOT), f'not valid JSON: {e}')
        return None


class Registry:
    def __init__(self, problems):
        path = os.path.join(ROOT, 'tools', 'quests', 'registry.json')
        data = load_json(path, problems) or {}
        self.sets = {k: set(v) for k, v in data.items() if isinstance(v, list)}
        self.extra_items = set()
        self.problems = problems

    def check(self, kind, ident, where, unchecked=False):
        if unchecked:
            return
        if not isinstance(ident, str) or ':' not in ident:
            self.problems.error(where, f'{SINGULAR[kind]} id {ident!r} needs a namespace, like minecraft:{ident}')
            return
        known = self.sets.get(kind, set())
        if kind == 'items':
            known = known | self.extra_items
        if ident not in known:
            path = ident.split(':', 1)[1]
            near = [k for k in known if k.split(':', 1)[1] == path][:3]
            near += [k for k in difflib.get_close_matches(ident, known, n=3, cutoff=0.8) if k not in near]
            hint = f' (did you mean {", ".join(near[:3])}?)' if near else ''
            self.problems.error(where, f'unknown {SINGULAR[kind]} {ident}{hint}. '
                                       'Add "unchecked": true if it only exists at runtime')
        if kind == 'items' and ident in self.sets.get('trimmed', set()):
            self.problems.error(where, f'{ident} is trimmed out of the pack (kubejs/startup_scripts/trimmed_items.js)')


# ---- tasks and rewards ----

def build_task(t, ids, reg, where, problems):
    """One task from its short form. Returns the FTB task, or None."""
    if not isinstance(t, dict):
        problems.error(where, f'a task must be an object, got {t!r}')
        return None
    task = {'id': fid(*ids)}
    unchecked = t.get('unchecked', False)
    if 'title' in t:
        task['title'] = t['title']
    if 'item' in t:
        reg.check('items', t['item'], where, unchecked)
        task.update(type='item', item=t['item'])
        if t.get('count', 1) != 1:
            task['count'] = L(t['count'])
        if t.get('consume'):
            task['consume_items'] = True
        if t.get('crafted'):
            task['only_from_crafting'] = True
    elif 'kill' in t:
        reg.check('entities', t['kill'], where, unchecked)
        task.update(type='kill', entity=t['kill'], value=L(t.get('count', 1)))
    elif 'biome' in t:
        reg.check('biomes', t['biome'], where, unchecked)
        task.update(type='biome', biome=t['biome'])
    elif 'structure' in t:
        reg.check('structures', t['structure'], where, unchecked)
        task.update(type='structure', structure=t['structure'])
    elif 'dimension' in t:
        reg.check('dimensions', t['dimension'], where, unchecked)
        task.update(type='dimension', dimension=t['dimension'])
    elif 'advancement' in t:
        reg.check('advancements', t['advancement'], where, unchecked)
        task.update(type='advancement', advancement=t['advancement'], criterion=t.get('criterion', ''))
    elif 'stage' in t:
        task.update(type='gamestage', stage=t['stage'])
    elif 'observe' in t:
        target = t['observe']
        kind = 'entity_type' if target in reg.sets.get('entities', ()) else 'block'
        if kind == 'block':
            reg.check('items', target, where, unchecked)
        task.update(type='observation', observe_type=kind, to_observe=target,
                    timer=L(t.get('ticks', 0)))
    elif 'levels' in t:
        task.update(type='xp', value=L(t['levels']), points=False)
    elif 'checkmark' in t:
        task.update(type='checkmark')
        if isinstance(t['checkmark'], str):
            task['title'] = t['checkmark']
    else:
        problems.error(where, f'unknown task {json.dumps(t)}; use item, kill, biome, structure, dimension, '
                              'advancement, stage, observe, levels or checkmark')
        return None
    return task


def build_reward(r, ids, ctx, where, problems):
    if not isinstance(r, dict):
        problems.error(where, f'a reward must be an object, got {r!r}')
        return None
    reward = {'id': fid(*ids)}
    reg = ctx['registry']
    if 'title' in r:
        reward['title'] = r['title']
    if 'item' in r:
        reg.check('items', r['item'], where, r.get('unchecked', False))
        reward.update(type='item', item=r['item'])
        if r.get('count', 1) != 1:
            reward['count'] = r['count']
    elif 'skill' in r:
        cat = r['skill']
        if cat not in ctx['skills']:
            problems.error(where, f'unknown skill {cat!r}; one of {", ".join(sorted(ctx["skills"]))}')
            return None
        amount = int(r.get('xp', 0))
        if amount <= 0:
            problems.error(where, 'a skill reward needs "xp" above 0')
            return None
        title, icon = ctx['skills'][cat]
        reward.update(type='command', command=f'/puffish_skills experience add {{p}} puffish_skills:{cat} {amount}',
                      elevate_perms=True, silent=True, icon=icon)
        reward.setdefault('title', f'+{amount} {title} XP')
    elif 'xp' in r:
        reward.update(type='xp', xp=int(r['xp']))
    elif 'levels' in r:
        reward.update(type='xp_levels', xp_levels=int(r['levels']))
    elif 'table' in r:
        if r['table'] not in ctx['tables']:
            problems.error(where, f'unknown reward table {r["table"]!r} (tools/quests/src/reward_tables/)')
            return None
        reward.update(type='random', table_id=L(int(ctx['tables'][r['table']], 16)))
    elif 'command' in r:
        reward.update(type='command', command=r['command'], elevate_perms=True, silent=r.get('silent', True))
        if 'title' not in r:
            problems.warn(where, 'command rewards should have a "title" so players know what they get')
    elif 'stage' in r:
        reward.update(type='gamestage', stage=r['stage'])
    else:
        problems.error(where, f'unknown reward {json.dumps(r)}; use item, skill, xp, levels, table, command or stage')
        return None
    if r.get('auto'):
        reward['auto'] = 'invisible' if r['auto'] == 'invisible' else 'enabled'
    return reward


# ---- quest givers ----

GIVER_KINDS = {'villager', 'entity', 'drop', 'item'}


def giver_stage(chapter, quest):
    return f'fq.{chapter}.{quest}'


def build_giver(g, chapter, qid, ctx, where, problems):
    kind = g.get('type')
    if kind not in GIVER_KINDS:
        problems.error(where, f'giver "type" must be one of {", ".join(sorted(GIVER_KINDS))}')
        return None
    lines = g.get('lines', [])
    if not isinstance(lines, list) or not all(isinstance(x, str) for x in lines):
        problems.error(where, 'giver "lines" must be a list of strings')
        return None
    out = {'quest': f'{chapter}:{qid}', 'stage': giver_stage(chapter, qid), 'type': kind, 'lines': lines,
           'accept': g.get('accept', 'Accept'), 'requires': [], 'name': g.get('name', '')}
    reg = ctx['registry']
    if kind in ('villager', 'entity'):
        out.update(match_target(kind, g, reg, where, problems))
    elif kind in ('drop', 'item'):
        item = quest_item_id(g, chapter, qid, ctx, where, problems)
        if not item:
            return None
        out['item'] = item
        out['consume'] = g.get('consume', True)
        if kind == 'drop':
            sources = g.get('from', [])
            if not sources:
                problems.error(where, 'a drop giver needs "from": [mob ids]')
            for s in sources:
                reg.check('entities', s, where, g.get('unchecked', False))
            out['from'] = sources
            out['chance'] = float(g.get('chance', 0.05))
            if not 0 < out['chance'] <= 1:
                problems.error(where, '"chance" must be between 0 and 1')
    for req in g.get('requires', []):
        out['requires'].append(giver_stage(*resolve_ref(req, chapter)) + '.done')
        ctx['done_stages'].add(resolve_ref(req, chapter))
    return out


def match_target(kind, g, reg, where, problems):
    """Which villager or mob this is: a villager by profession ("any" for all), or a mob type, optionally by name."""
    if kind == 'villager':
        prof = g.get('profession', 'any')
        if prof != 'any' and ':' not in prof:
            problems.error(where, f'villager profession needs a namespace, like minecraft:{prof}')
        return {'match': 'villager', 'profession': prof}
    reg.check('entities', g.get('entity'), where, g.get('unchecked', False))
    return {'match': 'entity', 'entity': g.get('entity'), 'named': g.get('named', '')}


def build_talk(t, chapter, qid, n, requires, ctx, where, problems):
    """A "talk to" task: done when the player sneak-right-clicks the right villager or mob while on the quest."""
    target = t.get('talk')
    if target not in ('villager', 'entity'):
        problems.error(where, '"talk" must be "villager" or "entity"')
        return None, None
    lines = t.get('lines', [])
    if not isinstance(lines, list) or not all(isinstance(x, str) for x in lines):
        problems.error(where, 'talk "lines" must be a list of strings')
        return None, None
    stage = f'{giver_stage(chapter, qid)}.talk{n}'
    entry = {'quest': f'{chapter}:{qid}', 'stage': stage, 'type': 'talk', 'lines': lines, 'requires': list(requires),
             'name': t.get('name', '')}
    entry.update(match_target(target, t, ctx['registry'], where, problems))
    default = 'Talk to a villager' if target == 'villager' else 'Talk to them'
    if target == 'villager' and entry['profession'] != 'any':
        default = 'Talk to a ' + entry['profession'].split(':', 1)[1].replace('_', ' ')
    task = {'id': fid('task', chapter, qid, str(n)), 'type': 'gamestage', 'stage': stage, 'title': t.get('title', default)}
    return task, entry


def quest_item_id(g, chapter, qid, ctx, where, problems):
    """Quest items given by drops or used to start quests. Either an existing item or a new kubejs:quest_* one."""
    if 'item' in g and isinstance(g['item'], str):
        ctx['registry'].check('items', g['item'], where, g.get('unchecked', False))
        return g['item']
    spec = g.get('item', {})
    if not isinstance(spec, dict) or 'name' not in spec:
        problems.error(where, 'needs "item": "<existing id>" or "item": {"name": "Torn Letter", ...}')
        return None
    key = spec.get('id', f'quest_{qid}')
    if not NAME.match(key):
        problems.error(where, f'quest item id {key!r} may only use a-z, 0-9 and _')
        return None
    item = f'kubejs:{key}'
    ctx['quest_items'][item] = {'id': key, 'name': spec['name'], 'texture': spec.get('texture', 'minecraft:item/paper'),
                                'tooltip': spec.get('tooltip', 'Right-click to read'), 'glow': spec.get('glow', True)}
    ctx['registry'].extra_items.add(item)
    return item


def resolve_ref(ref, chapter):
    return tuple(ref.split(':', 1)) if ':' in ref else (chapter, ref)


# ---- layout ----

def auto_layout(quests, deps):
    """Quests without "pos" go in columns by how many steps they are from the start, 1.5 apart."""
    depth = {}

    def d(q, seen=()):
        if q in depth:
            return depth[q]
        if q in seen:
            return 0
        local = [p for p in deps.get(q, []) if p in quests]
        depth[q] = 0 if not local else 1 + max(d(p, seen + (q,)) for p in local)
        return depth[q]

    for q in quests:
        d(q)
    columns = {}
    for q in quests:
        columns.setdefault(depth[q], []).append(q)
    pos = {}
    for col, members in columns.items():
        for i, q in enumerate(members):
            pos[q] = (col * 1.5, (i - (len(members) - 1) / 2) * 1.5)
    return pos


# ---- main ----

def main():
    check_only = '--check' in sys.argv
    problems = Problems()
    reg = Registry(problems)
    pack = load_json(os.path.join(SRC, 'pack.json'), problems) or {}
    skills = {}
    sk_cfg = load_json(os.path.join(ROOT, 'config', 'puffish_skills', 'config.json'), problems) or {}
    for cat in sk_cfg.get('categories', []):
        c = load_json(os.path.join(ROOT, 'config', 'puffish_skills', 'categories', cat, 'category.json'), problems) or {}
        skills[cat] = (c.get('title', cat), c.get('icon', {}).get('data', {}).get('item', 'minecraft:book'))
    ctx = {'registry': reg, 'skills': skills, 'tables': {}, 'quest_items': {}, 'done_stages': set()}

    # reward tables
    tables_out = {}
    tdir = os.path.join(SRC, 'reward_tables')
    for i, f in enumerate(sorted(os.listdir(tdir)) if os.path.isdir(tdir) else []):
        if not f.endswith('.json'):
            continue
        name = f[:-5]
        where = f'reward_tables/{f}'
        t = load_json(os.path.join(tdir, f), problems)
        if t is None:
            continue
        tid = fid('table', name)
        ctx['tables'][name] = tid
        entries = []
        for n, e in enumerate(t.get('rewards', [])):
            reg.check('items', e.get('item'), where, e.get('unchecked', False))
            entry = {'id': fid('table', name, str(n)), 'type': 'item', 'item': e.get('item')}
            if e.get('count', 1) != 1:
                entry['count'] = e['count']
            if e.get('weight', 1) != 1:
                entry['weight'] = float(e['weight'])
            entries.append(entry)
        if not entries:
            problems.error(where, 'a reward table needs "rewards": [{"item": ..., "weight": ...}]')
        tables_out[name] = {'id': tid, 'title': t.get('title', name), 'icon': t.get('icon', 'minecraft:chest'),
                            'loot_size': int(t.get('rolls', 1)), 'order_index': i, 'use_title': True,
                            'rewards': entries}

    # chapter groups
    groups = pack.get('groups', [])
    group_ids = {g['id']: fid('group', g['id']) for g in groups if 'id' in g}

    # chapters: first pass collects quest names so dependencies can point across chapters
    cdir = os.path.join(SRC, 'chapters')
    sources = []
    for f in sorted(os.listdir(cdir)) if os.path.isdir(cdir) else []:
        if f.endswith('.json'):
            c = load_json(os.path.join(cdir, f), problems)
            if c is not None:
                sources.append((f, c))
    known = {}
    for f, c in sources:
        name = f[:-5]
        if not NAME.match(name):
            problems.error(f'chapters/{f}', 'file names may only use a-z, 0-9 and _ (they become quest ids)')
        for q in c.get('quests', []):
            qid = q.get('id', '')
            if not NAME.match(qid):
                problems.error(f'chapters/{f}', f'quest id {qid!r} may only use a-z, 0-9 and _')
            if (name, qid) in known:
                problems.error(f'chapters/{f}', f'quest id {qid!r} is used twice')
            known[(name, qid)] = fid('quest', name, qid)

    chapters_out = {}
    givers = []
    for order, (f, c) in enumerate(sorted(sources, key=lambda s: (s[1].get('order', 0), s[0]))):
        name = f[:-5]
        cwhere = f'chapters/{f}'
        if c.get('group') and c['group'] not in group_ids:
            problems.error(cwhere, f'unknown group {c["group"]!r} (groups are listed in pack.json)')
        if 'icon' in c:
            reg.check('items', c['icon'], cwhere)
        quests = c.get('quests', [])
        deps = {q.get('id'): [resolve_ref(r, name) for r in q.get('after', [])] for q in quests}
        layout = auto_layout([q.get('id') for q in quests], {k: [p[1] for p in v if p[0] == name] for k, v in deps.items()})
        out_quests = []
        for q in quests:
            qid = q.get('id', '?')
            where = f'{cwhere} > {qid}'
            quest = {'id': known.get((name, qid), fid('quest', name, qid)), 'title': q.get('title', qid)}
            for k in ('subtitle',):
                if k in q:
                    quest[k] = q[k]
            text = q.get('text', [])
            if isinstance(text, str):
                text = [text]
            if text:
                quest['description'] = [p for para in text for p in (para, '')][:-1]
            if 'icon' in q:
                reg.check('items', q['icon'], where, q.get('unchecked_icon', False))
                quest['icon'] = q['icon']
            x, y = q.get('pos', layout.get(qid, (0, 0)))
            quest['x'], quest['y'] = D(x), D(y)
            if 'shape' in q:
                if q['shape'] not in SHAPES:
                    problems.error(where, f'shape must be one of {", ".join(sorted(SHAPES))}')
                quest['shape'] = q['shape']
            if 'size' in q:
                quest['size'] = D(q['size'])
            dep_ids = []
            for ref in deps.get(qid, []):
                if ref not in known:
                    problems.error(where, f'"after" points at unknown quest {":".join(ref)}')
                else:
                    dep_ids.append(known[ref])
            if dep_ids:
                quest['dependencies'] = dep_ids
                if q.get('after_any'):
                    quest['dependency_requirement'] = 'one_completed'
            hidden = q.get('hidden', False)
            if hidden == 'until_deps':
                quest['hide_until_deps_visible'] = True
            elif hidden not in (False, None):
                problems.error(where, 'hidden must be false or "until_deps" (quests with a giver hide themselves)')
            if q.get('optional'):
                quest['optional'] = True
            if 'repeat' in q:
                quest['can_repeat'] = True
            tasks = []
            giver = q.get('giver')
            if giver:
                g = build_giver(giver, name, qid, ctx, where + ' > giver', problems)
                if g:
                    givers.append(g)
                    tasks.append({'id': fid('task', name, qid, 'giver'), 'type': 'gamestage', 'stage': g['stage'],
                                  'title': giver.get('task', 'Accepted')})
                    quest['invisible'] = True
                    quest['invisible_until_tasks'] = 1
            if giver:
                talk_requires = [giver_stage(name, qid)]
            else:
                talk_requires = [giver_stage(*ref) + '.done' for ref in deps.get(qid, [])]
            for n, t in enumerate(q.get('tasks', [])):
                twhere = f'{where} > task {n + 1}'
                if isinstance(t, dict) and 'talk' in t:
                    task, entry = build_talk(t, name, qid, n, talk_requires, ctx, twhere, problems)
                    if entry:
                        if not giver:
                            ctx['done_stages'].update(deps.get(qid, []))
                        givers.append(entry)
                        talk_requires = talk_requires + [entry['stage']]
                else:
                    task = build_task(t, ('task', name, qid, str(n)), reg, twhere, problems)
                if task:
                    tasks.append(task)
            if not tasks:
                problems.error(where, 'a quest needs at least one task')
            quest['tasks'] = tasks
            rewards = []
            for n, r in enumerate(q.get('rewards', [])):
                reward = build_reward(r, ('reward', name, qid, str(n)), ctx, f'{where} > reward {n + 1}', problems)
                if reward:
                    rewards.append(reward)
            if rewards:
                quest['rewards'] = rewards
            out_quests.append((qid, quest))
        chapters_out[name] = {
            'id': fid('chapter', name), 'filename': name, 'title': c.get('title', name),
            'icon': c.get('icon', 'minecraft:book'), 'group': group_ids.get(c.get('group'), ''), 'order_index': order,
            'default_hide_dependency_lines': False, 'default_quest_shape': '', 'quest_links': [],
            'quests': out_quests,
        }
        if c.get('subtitle'):
            chapters_out[name]['subtitle'] = [c['subtitle']] if isinstance(c['subtitle'], str) else c['subtitle']

    # quests that a giver needs finished get an invisible stage reward when done
    for (cname, qid) in ctx['done_stages']:
        if cname not in chapters_out or qid not in dict(chapters_out[cname]['quests']):
            problems.error('givers', f'"requires" points at unknown quest {cname}:{qid}')
            continue
        quest = dict(chapters_out[cname]['quests'])[qid]
        quest.setdefault('rewards', []).append({'id': fid('reward', cname, qid, 'done'), 'type': 'gamestage',
                                                'stage': giver_stage(cname, qid) + '.done', 'auto': 'invisible'})
    for ch in chapters_out.values():
        ch['quests'] = [q for _, q in ch['quests']]

    for w in problems.warnings:
        print('warning: ' + w)
    if problems.errors:
        for e in problems.errors:
            print('error: ' + e)
        sys.exit(f'{len(problems.errors)} problem(s); nothing written')
    count = sum(len(c['quests']) for c in chapters_out.values())
    summary = f'{len(chapters_out)} chapters, {count} quests, {len(tables_out)} reward tables, {len(givers)} quest givers'
    if check_only:
        print('ok: ' + summary)
        return

    data = {
        'version': 13, 'title': pack.get('title', 'Quests'), 'icon': pack.get('icon', 'ftbquests:book'),
        'default_reward_team': False, 'default_consume_items': False, 'default_autoclaim_rewards': 'disabled',
        'default_quest_shape': pack.get('default_shape', 'circle'), 'default_quest_disable_jei': False,
        'detection_delay': 20, 'disable_gui': False, 'drop_loot_crates': False, 'emergency_items_cooldown': 300,
        'grid_scale': D(0.5), 'lock_message': '', 'pause_game': False, 'progression_mode': 'flexible',
        'loot_crate_no_drop': {'boss': 0, 'monster': 600, 'passive': 4000},
    }
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(os.path.join(OUT, 'chapters'))
    header = ''
    write(os.path.join(OUT, 'data.snbt'), header + snbt(data) + '\n')
    write(os.path.join(OUT, 'chapter_groups.snbt'),
          snbt({'chapter_groups': [{'id': group_ids[g['id']], 'title': g.get('title', g['id'])} for g in groups]}) + '\n')
    for name, ch in chapters_out.items():
        write(os.path.join(OUT, 'chapters', name + '.snbt'), snbt(ch) + '\n')
    if tables_out:
        os.makedirs(os.path.join(OUT, 'reward_tables'))
        for name, t in tables_out.items():
            write(os.path.join(OUT, 'reward_tables', name + '.snbt'), snbt(t) + '\n')

    note = '// Generated by tools/quests/make_quests.py from tools/quests/src. Do not edit; edit the sources and rerun.\n'
    items = sorted(ctx['quest_items'].values(), key=lambda i: i['id'])
    write(ITEMS_JS, note + '// Quest items: letters, notes and keepsakes that start quests (see quest_givers.js).\n'
          'StartupEvents.registry(\'item\', event => {\n' + ''.join(
              f"  event.create({json.dumps(i['id'])}).displayName({json.dumps(i['name'])}).texture({json.dumps(i['texture'])})"
              f".maxStackSize(1).tooltip({json.dumps(i['tooltip'])})" + ('.glow(true)' if i['glow'] else '') + '\n'
              for i in items) + '})\n')
    write(GIVERS_JS, '// priority: 100\n' + note +
          '// Who gives which quest. Read by quest_givers.js.\n'
          'global.QUEST_GIVERS = ' + json.dumps(givers, indent=2) + '\n')
    print('wrote ' + summary)


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(text)


if __name__ == '__main__':
    main()
