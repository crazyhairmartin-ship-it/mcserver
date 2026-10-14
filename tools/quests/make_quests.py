"""Builds the pack's FTB Quests book from the JSON sources in tools/quests/src.

    python tools/quests/make_quests.py          check everything and write the files
    python tools/quests/make_quests.py --check  check only, write nothing
    add --artifacts to list the artifacts that don't have a quest built around them yet

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
GROUPS_DIR = os.path.join(ROOT, 'kubejs', 'data', 'fotf', 'tags', 'worldgen', 'structure', 'groups')
NAME = re.compile(r'^[a-z0-9_]+$')
SIGNATURE_MODS = {'artifacts'}                          # items that each get one quest designed around them
SIGNATURE_EXEMPT = {'artifacts:mimic_spawn_egg'}
SINGULAR = {'items': 'item', 'entities': 'mob', 'enchantments': 'enchantment', 'biomes': 'biome', 'structures': 'structure',
            'advancements': 'advancement', 'dimensions': 'dimension'}
SHAPES = {'circle', 'square', 'rsquare', 'diamond', 'pentagon', 'hexagon', 'octagon', 'heart', 'gear'}


# ---- SNBT ----

class D(float):
    """A double (written 1.0d)."""


class L(int):
    """A long (written 4L)."""


class IA(list):
    """An int array (written [I; 1, 2, 3])."""


class B(int):
    """A byte (written 1b)."""


class S(int):
    """A short (written 5s)."""


def snbt(value, indent=0):
    tab = '\t'
    if isinstance(value, bool):
        return 'true' if value else 'false'
    if isinstance(value, D):
        return f'{float(value)!r}d'
    if isinstance(value, L):
        return f'{int(value)}L'
    if isinstance(value, B):
        return f'{int(value)}b'
    if isinstance(value, S):
        return f'{int(value)}s'
    if isinstance(value, (int, float)):
        return repr(value)
    if isinstance(value, str):
        return '"' + value.replace('\\', '\\\\').replace('"', '\\"') + '"'
    if isinstance(value, IA):
        return '[I; ' + ', '.join(str(int(v)) for v in value) + ']'
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

PLACES = {}
STRUCTURE_GROUPS = {}   # name -> structure ids, from src/structure_groups.json; written as #fotf:groups/<name>


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
        st = t['structure']
        if isinstance(st, str) and st.startswith('#') and ':' not in st:      # "#taverns": a structure group
            if st[1:] not in STRUCTURE_GROUPS:
                problems.error(where, f'unknown structure group {st}; groups are listed in tools/quests/src/structure_groups.json')
            st = 'fotf:groups/' + st[1:]
            task.update(type='structure', structure='#' + st)
        elif isinstance(st, str) and st.startswith('#'):                      # another structure tag, e.g. #minecraft:village
            task.update(type='structure', structure=st)
        else:
            reg.check('structures', st, where, unchecked)
            task.update(type='structure', structure=st)
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
    elif 'place' in t:
        place = PLACES.get(t['place'])
        if not place:
            problems.error(where, f'unknown place {t["place"]!r}; places are listed in tools/quests/src/places.json')
            return None
        x, y, z = place['pos']
        r = int(place.get('radius', 48))
        task.update(type='location', dimension=place.get('dimension', 'minecraft:overworld'), ignore_dimension=False,
                    position=IA([x - r, y - 32, z - r]), size=IA([2 * r, 96, 2 * r]))
        task.setdefault('title', 'Travel to ' + place.get('name', t['place']))
    elif 'stat' in t:
        stat = t['stat']
        if not isinstance(stat, str) or ':' not in stat:
            problems.error(where, f'stat {stat!r} needs a namespace, like minecraft:fish_caught')
        task.update(type='stat', stat=stat, value=int(t.get('count', 1)))
    elif 'checkmark' in t:
        task.update(type='checkmark')
        if isinstance(t['checkmark'], str):
            task['title'] = t['checkmark']
    else:
        problems.error(where, f'unknown task {json.dumps(t)}; use item, kill, biome, structure, dimension, '
                              'place, advancement, stage, observe, levels, stat, drop, talk or checkmark')
        return None
    return task


ITEM_EXTRAS = ('enchant', 'name', 'lore', 'unbreakable')


def text_json(text, color, italic):
    return json.dumps({'text': text, 'color': color, 'italic': italic}, ensure_ascii=False)


def item_value(r, reg, where, problems):
    """An item for a reward: a plain id, or with "enchant" {id: level}, "name", "lore" [lines], "unbreakable".
    Named items show their name in gold; enchanted books store their enchantments the way books do."""
    item = r['item']
    reg.check('items', item, where, r.get('unchecked', False))
    if not any(k in r for k in ITEM_EXTRAS):
        return item
    tag = {}
    enchants = r.get('enchant', {})
    if not isinstance(enchants, dict):
        problems.error(where, '"enchant" must be an object like {"minecraft:sharpness": 5}')
        enchants = {}
    if enchants:
        for ench, lvl in enchants.items():
            reg.check('enchantments', ench, where, r.get('unchecked', False))
            if not isinstance(lvl, int) or not 1 <= lvl <= 255:
                problems.error(where, f'enchantment level for {ench} must be a whole number 1-255')
        key = 'StoredEnchantments' if item == 'minecraft:enchanted_book' else 'Enchantments'
        tag[key] = [{'id': ench, 'lvl': S(lvl)} for ench, lvl in enchants.items()]
    display = {}
    if 'name' in r:
        display['Name'] = text_json(r['name'], 'gold', False)
    if 'lore' in r:
        lore = [r['lore']] if isinstance(r['lore'], str) else r['lore']
        display['Lore'] = [text_json(line, 'gray', True) for line in lore]
    if display:
        tag['display'] = display
    if r.get('unbreakable'):
        tag['Unbreakable'] = B(1)
    return {'id': item, 'Count': B(1), 'tag': tag}


def build_reward(r, ids, ctx, where, problems):
    if not isinstance(r, dict):
        problems.error(where, f'a reward must be an object, got {r!r}')
        return None
    reward = {'id': fid(*ids)}
    reg = ctx['registry']
    if 'title' in r:
        reward['title'] = r['title']
    if 'item' in r:
        reward.update(type='item', item=item_value(r, reg, where, problems))
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

GIVER_KINDS = {'villager', 'entity', 'org', 'character', 'drop', 'item'}
TARGET_KINDS = ('villager', 'entity', 'org', 'character')


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
    if kind in TARGET_KINDS:
        out.update(match_target(kind, g, ctx, where, problems))
        if g.get('pool'):
            if not NAME.match(str(g['pool'])):
                problems.error(where, '"pool" must be an a-z_ name')
            out['pool'] = g['pool']
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


def match_target(kind, g, ctx, where, problems):
    """Who this is: a villager by profession ("any" for all), a mob type (optionally by name), any representative of
    an organisation (pack.json "organisations"), or a named character (pack.json "characters")."""
    reg = ctx['registry']
    if kind == 'org':
        org = ctx['orgs'].get(g.get('org'))
        if not org:
            problems.error(where, f'unknown organisation {g.get("org")!r} (pack.json "organisations")')
            return {'match': 'org', 'org': g.get('org'), 'professions': [], 'org_name': ''}
        return {'match': 'org', 'org': g['org'], 'professions': org['professions'], 'org_name': org['name']}
    if kind == 'character':
        if g.get('character') not in ctx['characters']:
            problems.error(where, f'unknown character {g.get("character")!r} (pack.json "characters")')
        return {'match': 'character', 'character': g.get('character')}
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
    if target not in TARGET_KINDS:
        problems.error(where, '"talk" must be "villager", "entity", "org" or "character"')
        return None, None
    lines = t.get('lines', [])
    if not isinstance(lines, list) or not all(isinstance(x, str) for x in lines):
        problems.error(where, 'talk "lines" must be a list of strings')
        return None, None
    stage = f'{giver_stage(chapter, qid)}.talk{n}'
    entry = {'quest': f'{chapter}:{qid}', 'stage': stage, 'type': 'talk', 'lines': lines, 'requires': list(requires),
             'name': t.get('name', '')}
    entry.update(match_target(target, t, ctx, where, problems))
    default = 'Talk to a villager' if target == 'villager' else 'Talk to them'
    if target == 'villager' and entry['profession'] != 'any':
        default = 'Talk to a ' + entry['profession'].split(':', 1)[1].replace('_', ' ')
    elif target == 'org':
        default = 'Talk to a representative of the ' + entry.get('org_name', '')
    elif target == 'character' and entry['character'] in ctx['characters']:
        default = 'Talk to ' + ctx['characters'][entry['character']]['name']
    task = {'id': fid('task', chapter, qid, str(n)), 'type': 'gamestage', 'stage': stage, 'title': t.get('title', default)}
    return task, entry


def place_box(place):
    x, y, z = place['pos']
    r = int(place.get('radius', 48))
    return {'dimension': place.get('dimension', 'minecraft:overworld'), 'min': [x - r, y - 32, z - r],
            'max': [x + r, y + 64, z + r]}


def build_encounter(t, chapter, qid, n, quest_id, prev_tasks, ctx, where, problems):
    """An "encounter" task: when the step opens, a character or mob appears near the player; talking to it (or
    defeating it) completes the step. Optional "where" conditions say where it can happen."""
    spec = t['encounter']
    if not isinstance(spec, dict):
        problems.error(where, '"encounter" must be an object')
        return None, None
    reg = ctx['registry']
    then = spec.get('then', 'talk')
    if then not in ('talk', 'kill', 'escort'):
        problems.error(where, 'encounter "then" must be "talk", "kill" or "escort"')
    entry = {'quest': f'{chapter}:{qid}', 'stage': f'{giver_stage(chapter, qid)}.enc{n}', 'type': 'encounter',
             'then': then, 'lines': spec.get('lines', []), 'arrive': spec.get('arrive', ''), 'requires': [],
             'quest_id': quest_id, 'prev_tasks': list(prev_tasks), 'name': spec.get('name', ''),
             'distance': spec.get('distance', [8, 16]), 'minutes': float(spec.get('minutes', 20)),
             'health': spec.get('health'), 'glow': bool(spec.get('glow', False)), 'where': {}}
    if 'character' in spec:
        char = ctx['characters'].get(spec['character'])
        if not char:
            problems.error(where, f'unknown character {spec["character"]!r} (pack.json "characters")')
            return None, None
        entry.update(entity=char['entity'], name=entry['name'] or char['name'], profession=char.get('profession', ''))
    elif 'entity' in spec:
        reg.check('entities', spec['entity'], where, spec.get('unchecked', False))
        entry.update(entity=spec['entity'], profession=spec.get('profession', ''))
    else:
        problems.error(where, 'an encounter needs "character" or "entity"')
        return None, None
    if not entry['name']:
        problems.error(where, 'an encounter needs a "name" (or a character, which has one)')
    cond = spec.get('where', {})
    for b in cond.get('biomes', []):
        reg.check('biomes', b, where, spec.get('unchecked', False))
    if cond.get('dimension'):
        reg.check('dimensions', cond['dimension'], where)
    entry['where'] = {k: cond[k] for k in ('biomes', 'dimension', 'below_y', 'above_y') if k in cond}
    if then == 'escort':
        dest = build_destination(spec.get('to'), reg, where, problems)
        if dest:
            entry['to'] = dest
        entry['thanks'] = spec.get('thanks', [])
    verb = {'talk': 'Meet ', 'kill': 'Defeat ', 'escort': 'Escort '}.get(then, 'Meet ')
    title = t.get('title', verb + entry['name'] + (' to ' + entry['to']['label'] if entry.get('to') else ''))
    task = {'id': fid('task', chapter, qid, str(n)), 'type': 'gamestage', 'stage': entry['stage'], 'title': title}
    return task, entry


# shortcuts a timed challenge can switch off (kubejs/server_scripts/quest_npcs.js)
TIMED_BANS = ('teleport', 'mounts', 'elytra', 'pearls', 'hurt')  # never grappling hooks: Dylan wants them allowed


def build_timed(t, chapter, qid, n, quest_id, prev_tasks, ctx, where, problems):
    """A "timed" challenge: when the step opens the player gets a [Start] button; they then have "seconds" to reach
    the goal: kill a number of a mob, raise a statistic by a number, or reach a place."""
    spec = t['timed']
    if not isinstance(spec, dict) or not isinstance(spec.get('goal'), dict):
        problems.error(where, '"timed" needs "seconds" and a "goal"')
        return None, None
    seconds = int(spec.get('seconds', 0))
    if seconds <= 0:
        problems.error(where, 'a timed challenge needs "seconds" above 0')
    goal = spec['goal']
    out_goal = {}
    if 'kill' in goal:
        ctx['registry'].check('entities', goal['kill'], where, goal.get('unchecked', False))
        out_goal = {'kind': 'kill', 'entity': goal['kill'], 'count': int(goal.get('count', 1))}
    elif 'stat' in goal:
        if ':' not in str(goal['stat']):
            problems.error(where, 'goal stat needs a namespace, like minecraft:fish_caught')
        out_goal = {'kind': 'stat', 'stat': goal['stat'], 'count': int(goal.get('count', 1))}
    elif 'place' in goal:
        if goal['place'] not in PLACES:
            problems.error(where, f'unknown place {goal["place"]!r} (tools/quests/src/places.json)')
            return None, None
        out_goal = {'kind': 'place', 'box': place_box(PLACES[goal['place']]),
                    'label': PLACES[goal['place']].get('name', goal['place'])}
    elif 'hold' in goal:
        hold = goal['hold'] if isinstance(goal['hold'], dict) else {}
        out_goal = {'kind': 'hold', 'radius': float(hold.get('radius', 8))}
    elif 'structure' in goal:
        dest = build_destination({'structure': goal['structure'], 'label': goal.get('label', 'the destination')},
                                 ctx['registry'], where, problems)
        if not dest:
            return None, None
        out_goal = dict(dest)
    else:
        problems.error(where, 'timed goal must be "kill", "stat", "place", "structure" or "hold"')
        return None, None
    if 'away' in goal:
        if out_goal.get('kind') not in ('place', 'structure'):
            problems.error(where, '"away" only works with a "place" or "structure" goal')
        else:
            out_goal['away'] = int(goal['away'])
    waves = []
    for w in spec.get('waves', []):
        if not isinstance(w, dict) or 'entity' not in w:
            problems.error(where, 'each wave needs an "entity" (and "count", "every" seconds)')
            continue
        ctx['registry'].check('entities', w['entity'], where, w.get('unchecked', False))
        waves.append({'entity': w['entity'], 'count': int(w.get('count', 3)), 'every': int(w.get('every', 20))})
    banned = spec.get('no', [])
    banned = banned if isinstance(banned, list) else [banned]
    for b in banned:
        if b not in TIMED_BANS:
            problems.error(where, f'timed "no": unknown shortcut {b!r} (one of {", ".join(TIMED_BANS)})')
    entry = {'quest': f'{chapter}:{qid}', 'stage': f'{giver_stage(chapter, qid)}.timed{n}', 'type': 'timed',
             'seconds': seconds, 'goal': out_goal, 'no': [b for b in banned if b in TIMED_BANS], 'waves': waves, 'lines': spec.get('lines', []), 'start': spec.get('start', 'Start'),
             'requires': [], 'quest_id': quest_id, 'prev_tasks': list(prev_tasks), 'name': spec.get('name', '')}
    task = {'id': fid('task', chapter, qid, str(n)), 'type': 'gamestage', 'stage': entry['stage'],
            'title': t.get('title', f'Challenge ({seconds // 60}:{seconds % 60:02d})')}
    return task, entry


def protect_specs(value):
    """A quest's "protect": one {"structure"/"structures", "blocks"} or a list of them."""
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def build_protect(spec, reg, where, problems):
    """Puzzle blocks: inside the structures, the blocks can't be broken by survival players, blown up or pushed by
    pistons. Structures are ids, "#group" (src/structure_groups.json, expanded here) or "#namespace:tag"; blocks are
    ids (checked as items unless "unchecked": true) or "#namespace:tag"."""
    if not isinstance(spec, dict):
        problems.error(where, '"protect" needs {"structure": ..., "blocks": [...]}')
        return None
    structures = spec.get('structures', spec.get('structure'))
    structures = structures if isinstance(structures, list) else [structures] if structures else []
    blocks = spec.get('blocks', [])
    blocks = blocks if isinstance(blocks, list) else [blocks]
    if not structures or not blocks:
        problems.error(where, '"protect" needs at least one structure and one block')
        return None
    out_structures = expand_structures(structures, reg, where, problems)
    for b in blocks:
        if not (isinstance(b, str) and b.startswith('#')):
            reg.check('items', b, where, spec.get('unchecked', False))
    rule = {'structures': out_structures, 'blocks': list(blocks)}
    minutes = spec.get('reset_minutes', 0)
    if minutes:
        rule['reset'] = int(float(minutes) * 60)
    return rule


def expand_structures(structures, reg, where, problems):
    """Structure ids, "#group" (src/structure_groups.json, expanded) or "#namespace:tag" (kept as is)."""
    out = []
    for sid in structures if isinstance(structures, list) else [structures]:
        if isinstance(sid, str) and sid.startswith('#') and ':' not in sid:
            if sid[1:] not in STRUCTURE_GROUPS:
                problems.error(where, f'unknown structure group {sid} (tools/quests/src/structure_groups.json)')
                continue
            out += STRUCTURE_GROUPS[sid[1:]]
        elif isinstance(sid, str) and sid.startswith('#'):
            out.append(sid)
        else:
            reg.check('structures', sid, where)
            out.append(sid)
    return sorted(set(out))


def build_destination(to, reg, where, problems):
    """Where an escort or timed goal is headed: {"place": id} or {"structure": id / "#group" / "#ns:tag"}."""
    if isinstance(to, dict) and 'place' in to:
        if to['place'] not in PLACES:
            problems.error(where, f'unknown place {to["place"]!r} (tools/quests/src/places.json)')
            return None
        return {'kind': 'place', 'box': place_box(PLACES[to['place']]), 'label': PLACES[to['place']].get('name', to['place'])}
    if isinstance(to, dict) and 'structure' in to:
        structures = expand_structures(to['structure'], reg, where, problems)
        if not structures:
            return None
        return {'kind': 'structure', 'structures': structures, 'label': to.get('label', 'the destination')}
    problems.error(where, 'a destination needs {"place": id} or {"structure": id}')
    return None


def build_build(t, chapter, qid, n, quest_id, prev_tasks, ctx, where, problems):
    """A "build" task: done when the blocks are within "radius" of the player (checked every few seconds while the
    step is open). "blocks": {"minecraft:campfire": 1, "#minecraft:logs": 20}."""
    spec = t['build']
    blocks = spec.get('blocks') if isinstance(spec, dict) else None
    if not isinstance(blocks, dict) or not blocks:
        problems.error(where, '"build" needs "blocks": {"id or #tag": count}')
        return None, None
    for b in blocks:
        if not b.startswith('#'):
            ctx['registry'].check('items', b, where, spec.get('unchecked', False))
    radius = int(spec.get('radius', 8))
    if not 1 <= radius <= 12:
        problems.error(where, '"build" radius must be 1-12')
    entry = {'quest': f'{chapter}:{qid}', 'stage': f'{giver_stage(chapter, qid)}.build{n}', 'type': 'build',
             'keys': list(blocks), 'counts': [int(v) for v in blocks.values()], 'radius': radius, 'requires': [],
             'quest_id': quest_id, 'prev_tasks': list(prev_tasks)}
    task = {'id': fid('task', chapter, qid, str(n)), 'type': 'gamestage', 'stage': entry['stage'],
            'title': t.get('title', 'Build it')}
    return task, entry


def build_photo(t, chapter, qid, n, quest_id, prev_tasks, ctx, where, problems):
    """A "photo" task (Camerapture): done when the player takes a picture while the quest is open and the subject is
    right: {"entity": id} (under the crosshair, or within 8 blocks), {"structure": id/#group}, {"biome": id} or
    {"place": id} (standing there). Add "label" for the task title ("the lighthouse")."""
    spec = t['photo']
    reg = ctx['registry']
    if not isinstance(spec, dict):
        problems.error(where, '"photo" needs {"entity"|"structure"|"biome"|"place": ...}')
        return None, None
    target = None
    if 'entity' in spec:
        reg.check('entities', spec['entity'], where, spec.get('unchecked', False))
        target = {'kind': 'entity', 'entity': spec['entity'], 'distance': float(spec.get('distance', 24))}
    elif 'biome' in spec:
        reg.check('biomes', spec['biome'], where, spec.get('unchecked', False))
        target = {'kind': 'biome', 'biome': spec['biome']}
    elif 'structure' in spec or 'place' in spec:
        target = build_destination({k: spec[k] for k in ('structure', 'place', 'label') if k in spec}, reg, where, problems)
    if not target:
        problems.error(where, '"photo" needs one of "entity", "structure", "biome" or "place"')
        return None, None
    label = spec.get('label') or spec.get('entity') or spec.get('biome') or target.get('label', 'it')
    entry = {'quest': f'{chapter}:{qid}', 'stage': f'{giver_stage(chapter, qid)}.photo{n}', 'type': 'photo',
             'target': target, 'requires': [], 'quest_id': quest_id, 'prev_tasks': list(prev_tasks)}
    task = {'id': fid('task', chapter, qid, str(n)), 'type': 'gamestage', 'stage': entry['stage'],
            'title': t.get('title', 'Take a photo of ' + str(label).split(':')[-1].replace('_', ' '))}
    return task, entry


def build_animal(t, kind, chapter, qid, n, quest_id, prev_tasks, ctx, where, problems):
    """A "tame" or "breed" task: done when the player tames (an animal becomes theirs) or breeds "count" of the mob(s)
    while the step is open. {"tame": "minecraft:wolf"} or {"tame": ["minecraft:horse", "minecraft:donkey"], "count": 2}."""
    mobs = t[kind]
    mobs = mobs if isinstance(mobs, list) else [mobs]
    if not mobs:
        problems.error(where, f'"{kind}" needs a mob id or a list of them')
        return None, None
    for m in mobs:
        ctx['registry'].check('entities', m, where, t.get('unchecked', False))
    count = int(t.get('count', 1))
    entry = {'quest': f'{chapter}:{qid}', 'stage': f'{giver_stage(chapter, qid)}.{kind}{n}', 'type': kind,
             'entities': list(mobs), 'count': count, 'requires': [], 'quest_id': quest_id,
             'prev_tasks': list(prev_tasks)}
    name = mobs[0].split(':')[-1].replace('_', ' ')
    verb = 'Tame' if kind == 'tame' else 'Breed'
    title = t.get('title', f'{verb} {count} {name}s' if count > 1 else f'{verb} a {name}')
    task = {'id': fid('task', chapter, qid, str(n)), 'type': 'gamestage', 'stage': entry['stage'], 'title': title}
    return task, entry


def build_waystones(t, chapter, qid, n, quest_id, prev_tasks, ctx, where, problems):
    """A "waystones" task: the player attunes this many waystones they didn't have when the step opened.
    {"waystones": 3, "wild": true} counts only waystones found in the wild (not villages or player-made)."""
    count = int(t['waystones'])
    if count < 1:
        problems.error(where, '"waystones" needs a count of 1 or more')
    entry = {'quest': f'{chapter}:{qid}', 'stage': f'{giver_stage(chapter, qid)}.waystones{n}', 'type': 'waystones',
             'count': count, 'wild': bool(t.get('wild', False)), 'requires': [], 'quest_id': quest_id,
             'prev_tasks': list(prev_tasks)}
    default = f'Attune {count} {"wild " if entry["wild"] else ""}waystone{"s" if count > 1 else ""}'
    task = {'id': fid('task', chapter, qid, str(n)), 'type': 'gamestage', 'stage': entry['stage'],
            'title': t.get('title', default)}
    return task, entry


def build_cast(t, chapter, qid, n, quest_id, prev_tasks, ctx, where, problems):
    """A "cast" task (Iron's Spells): cast spells while the step is open. {"cast": "any", "count": 100},
    {"cast": "irons_spellbooks:firebolt", "count": 20} or {"cast": {"school": "irons_spellbooks:fire"}, "count": 20}."""
    spec = t['cast']
    if isinstance(spec, dict):
        school = spec.get('school', '')
        spell = ''
        if not school:
            problems.error(where, '"cast" as an object needs "school", like irons_spellbooks:fire')
    else:
        school, spell = '', '' if spec == 'any' else str(spec)
        if spell and ':' not in spell:
            problems.error(where, f'spell id {spell!r} needs a namespace, like irons_spellbooks:{spell}')
    count = int(t.get('count', 1))
    entry = {'quest': f'{chapter}:{qid}', 'stage': f'{giver_stage(chapter, qid)}.cast{n}', 'type': 'cast',
             'spell': spell, 'school': school, 'count': count, 'requires': [], 'quest_id': quest_id,
             'prev_tasks': list(prev_tasks)}
    what = spell.split(':')[-1].replace('_', ' ') if spell else (school.split(':')[-1] + ' spells' if school else 'spells')
    task = {'id': fid('task', chapter, qid, str(n)), 'type': 'gamestage', 'stage': entry['stage'],
            'title': t.get('title', f'Cast {what} {count} time{"s" if count > 1 else ""}' if spell else f'Cast {count} {what}')}
    return task, entry


def build_task_drop(t, chapter, qid, n, quest_id, open_task, requires, ctx, where, problems):
    """A "unique drop" task: while the quest is open, the listed mobs can drop a quest item (or, with "fishing" in "from",
    it can be fished up); the task is to bring it."""
    spec = t['drop']
    if not isinstance(spec, dict):
        problems.error(where, '"drop" must be an object with "from", "chance" and "item"')
        return None, None
    sources = spec.get('from', [])
    if not sources:
        problems.error(where, 'a drop task needs "from": [mob ids]')
    for src in sources:
        if src != 'fishing':        # "fishing": the item can be fished up instead of dropped by a mob
            ctx['registry'].check('entities', src, where, spec.get('unchecked', False))
    chance = float(spec.get('chance', 0.25))
    if not 0 < chance <= 1:
        problems.error(where, '"chance" must be between 0 and 1')
    item_spec = spec.get('item')
    if isinstance(item_spec, dict):
        item_spec = dict(item_spec)
        item_spec.setdefault('tooltip', 'Quest item')
    item = quest_item_id(dict(spec, item=item_spec), chapter, f'{qid}_{n}', ctx, where, problems)
    if not item:
        return None, None
    count = int(t.get('count', 1))
    task = {'id': fid('task', chapter, qid, str(n)), 'type': 'item', 'item': item}
    if count != 1:
        task['count'] = L(count)
    if t.get('consume', True):
        task['consume_items'] = True
    if 'title' in t:
        task['title'] = t['title']
    entry = {'quest': f'{chapter}:{qid}', 'stage': '', 'type': 'task_drop', 'from': sources, 'chance': chance,
             'item': item, 'requires': list(requires), 'quest_id': quest_id, 'open_task': open_task, 'lines': [],
             'name': ''}
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
    places_path = os.path.join(SRC, 'places.json')
    places = (load_json(places_path, problems) or {}) if os.path.exists(places_path) else {}
    for key, place in places.items():
        if key.startswith('_'):
            continue
        pos = place.get('pos') if isinstance(place, dict) else None
        if not NAME.match(key) or not (isinstance(pos, list) and len(pos) == 3 and all(isinstance(v, int) for v in pos)):
            problems.error('places.json', f'place {key!r} needs an a-z_ id and "pos": [x, y, z] (whole numbers)')
            continue
        if place.get('dimension') and place['dimension'] not in reg.sets.get('dimensions', set()):
            problems.error('places.json', f'place {key!r}: unknown dimension {place["dimension"]}')
        PLACES[key] = place
    groups_path = os.path.join(SRC, 'structure_groups.json')
    for key, g in ((load_json(groups_path, problems) or {}) if os.path.exists(groups_path) else {}).items():
        if key.startswith('_'):
            continue
        members = g.get('structures') if isinstance(g, dict) else g
        if not NAME.match(key) or not isinstance(members, list) or not members:
            problems.error('structure_groups.json', f'group {key!r} needs an a-z_ name and a list of "structures"')
            continue
        for sid in members:
            reg.check('structures', sid, f'structure_groups.json > {key}')
        STRUCTURE_GROUPS[key] = members
    orgs, characters = {}, {}
    for o in pack.get('organisations', []):
        profs = o.get('professions', [])
        if not NAME.match(str(o.get('id', ''))) or not profs or not all(':' in p for p in profs):
            problems.error('pack.json', f'organisation {o.get("id")!r} needs an a-z_ id and namespaced "professions"')
            continue
        orgs[o['id']] = {'name': o.get('name', o['id']), 'professions': profs}
    for cid, c in pack.get('characters', {}).items():
        if cid.startswith('_'):
            continue
        if not NAME.match(cid) or not isinstance(c, dict) or 'name' not in c:
            problems.error('pack.json', f'character {cid!r} needs an a-z_ id and a "name"')
            continue
        c = dict(c)
        c.setdefault('entity', 'minecraft:villager')
        reg.check('entities', c['entity'], f'pack.json > character {cid}', c.get('unchecked', False))
        characters[cid] = c
    ctx = {'registry': reg, 'skills': skills, 'orgs': orgs, 'characters': characters, 'signatures': {},
           'artifact_rewards': [], 'protect': [], 'tables': {}, 'quest_items': {}, 'done_stages': set()}

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
            if 'item' not in e:
                problems.error(where, f'reward {n + 1} needs an "item"')
                continue
            if isinstance(e.get('item'), str) and e['item'].split(':')[0] in SIGNATURE_MODS \
                    and e['item'] not in SIGNATURE_EXEMPT:
                problems.warn(where, f'{e["item"]} in a random table: artifacts should come from the quest built '
                                     'around them')
            entry = {'id': fid('table', name, str(n)), 'type': 'item', 'item': item_value(e, reg, where, problems)}
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
            discover = q.get('discover')
            if discover is not None:
                if giver:
                    problems.error(where, 'a quest can have a "giver" or "discover", not both')
                trigger = build_task(discover, ('task', name, qid, 'discover'), reg, where + ' > discover', problems)
                if trigger:
                    trigger.setdefault('title', 'Discovered')
                    tasks.append(trigger)
                    quest['invisible'] = True
                    quest['invisible_until_tasks'] = 1
            if giver:
                g = build_giver(giver, name, qid, ctx, where + ' > giver', problems)
                if g:
                    givers.append(g)
                    tasks.append({'id': fid('task', name, qid, 'giver'), 'type': 'gamestage', 'stage': g['stage'],
                                  'title': giver.get('task', 'Accepted')})
                    quest['invisible'] = True
                    quest['invisible_until_tasks'] = 1
            # talk steps only answer while the quest is open: checked live against FTB Quests (quest_id/open_task)
            talk_requires = [giver_stage(name, qid)] if giver else []
            open_task = tasks[0]['id'] if tasks else ''
            for n, t in enumerate(q.get('tasks', [])):
                twhere = f'{where} > task {n + 1}'
                if isinstance(t, dict) and 'encounter' in t:
                    task, entry = build_encounter(t, name, qid, n, quest['id'], [x['id'] for x in tasks], ctx,
                                                  twhere, problems)
                    if entry:
                        givers.append(entry)
                elif isinstance(t, dict) and 'timed' in t:
                    task, entry = build_timed(t, name, qid, n, quest['id'], [x['id'] for x in tasks], ctx, twhere,
                                              problems)
                    if entry:
                        givers.append(entry)
                elif isinstance(t, dict) and 'cast' in t:
                    task, entry = build_cast(t, name, qid, n, quest['id'], [x['id'] for x in tasks], ctx, twhere,
                                             problems)
                    if entry:
                        givers.append(entry)
                elif isinstance(t, dict) and 'waystones' in t:
                    task, entry = build_waystones(t, name, qid, n, quest['id'], [x['id'] for x in tasks], ctx, twhere,
                                                  problems)
                    if entry:
                        givers.append(entry)
                elif isinstance(t, dict) and ('tame' in t or 'breed' in t):
                    task, entry = build_animal(t, 'tame' if 'tame' in t else 'breed', name, qid, n, quest['id'],
                                               [x['id'] for x in tasks], ctx, twhere, problems)
                    if entry:
                        givers.append(entry)
                elif isinstance(t, dict) and 'photo' in t:
                    task, entry = build_photo(t, name, qid, n, quest['id'], [x['id'] for x in tasks], ctx, twhere,
                                              problems)
                    if entry:
                        givers.append(entry)
                elif isinstance(t, dict) and 'build' in t:
                    task, entry = build_build(t, name, qid, n, quest['id'], [x['id'] for x in tasks], ctx, twhere,
                                              problems)
                    if entry:
                        givers.append(entry)
                elif isinstance(t, dict) and 'drop' in t:
                    task, entry = build_task_drop(t, name, qid, n, quest['id'], open_task, talk_requires, ctx, twhere,
                                                  problems)
                    if entry:
                        givers.append(entry)
                elif isinstance(t, dict) and 'talk' in t:
                    task, entry = build_talk(t, name, qid, n, talk_requires, ctx, twhere, problems)
                    if entry:
                        entry['quest_id'] = quest['id']
                        entry['open_task'] = open_task
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
            # artifact quests are built backwards from their artifact: the quest names it as its "signature"
            sig = q.get('signature')
            if sig is not None:
                reg.check('items', sig, where + ' > signature')
                if sig in ctx['signatures']:
                    problems.error(where, f'{sig} is already the signature of {ctx["signatures"][sig]}; '
                                          'each artifact gets one quest built around it')
                ctx['signatures'][sig] = f'{name}:{qid}'
            for n, spec in enumerate(protect_specs(q.get('protect'))):
                rule = build_protect(spec, reg, f'{where} > protect {n + 1}', problems)
                if rule:
                    ctx['protect'].append(rule)
            for r in q.get('rewards', []):
                item = r.get('item') if isinstance(r, dict) else None
                if isinstance(item, str) and item.split(':')[0] in SIGNATURE_MODS and item not in SIGNATURE_EXEMPT:
                    ctx['artifact_rewards'].append((f'{name}:{qid}', item))
                    if item != sig:
                        problems.warn(where, f'gives {item} without being built around it (add "signature": '
                                             f'"{item}" to the quest that is designed for it)')
            out_quests.append((qid, quest))
        links = []
        for n, link in enumerate(c.get('links', [])):
            lwhere = f'{cwhere} > link {n + 1}'
            ref = resolve_ref(link.get('to', ''), name)
            if ref not in known:
                problems.error(lwhere, f'"to" points at unknown quest {":".join(ref)}')
                continue
            lx, ly = link.get('pos', (0, 0))
            entry = {'id': fid('link', name, str(n)), 'linked_quest': known[ref], 'x': D(lx), 'y': D(ly)}
            if 'shape' in link:
                entry['shape'] = link['shape']
            if 'size' in link:
                entry['size'] = D(link['size'])
            links.append(entry)
        chapters_out[name] = {
            'id': fid('chapter', name), 'filename': name, 'title': c.get('title', name),
            'icon': c.get('icon', 'minecraft:book'), 'group': group_ids.get(c.get('group'), ''), 'order_index': order,
            'default_hide_dependency_lines': False, 'default_quest_shape': '', 'quest_links': links,
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
    for cid, char in characters.items():
        offers = []
        for n, o in enumerate(char.get('shop', [])):
            swhere = f'pack.json > character {cid} > shop {n + 1}'
            if not isinstance(o, dict) or not isinstance(o.get('give'), dict) or not o.get('cost'):
                problems.error(swhere, 'a shop offer needs "cost": [{"item", "count"}] and "give": {"item", "count"}')
                continue
            for c in o['cost'] + [o['give']]:
                reg.check('items', c.get('item'), swhere, c.get('unchecked', False))
            offer = {'cost': [{'item': c['item'], 'count': int(c.get('count', 1))} for c in o['cost']],
                     'give': dict(o['give']), 'quest_id': '', 'requires': o.get('requires', '')}
            offer['give']['count'] = int(offer['give'].get('count', 1))
            if o.get('requires'):
                ref = tuple(o['requires'].split(':', 1)) if ':' in o['requires'] else None
                if ref not in known:
                    problems.error(swhere, f'"requires" points at unknown quest {o["requires"]!r} (chapter:quest)')
                    continue
                offer['quest_id'] = known[ref]
            offers.append(offer)
        if 'shop' in char:
            char['shop'] = offers
    if problems.errors:
        for e in problems.errors:
            print('error: ' + e)
        sys.exit(f'{len(problems.errors)} problem(s); nothing written')
    count = sum(len(c['quests']) for c in chapters_out.values())
    summary = f'{len(chapters_out)} chapters, {count} quests, {len(tables_out)} reward tables, {len(givers)} quest givers'
    all_artifacts = sorted(i for i in reg.sets.get('items', set())
                           if i.split(':')[0] in SIGNATURE_MODS and i not in SIGNATURE_EXEMPT
                           and not i.startswith('artifacts:umbrella_'))   # umbrella_* are model variants
    summary += f', {len(ctx["signatures"])}/{len(all_artifacts)} artifacts with a quest built around them'
    if '--artifacts' in sys.argv:
        missing = [a for a in all_artifacts if a not in ctx['signatures']]
        print('artifacts without a signature quest: ' + (', '.join(missing) or 'none'))
    if check_only:
        print('ok: ' + summary)
        return

    data = {
        'version': 13, 'title': pack.get('title', 'Quests'), 'icon': pack.get('icon', 'ftbquests:book'),
        'default_reward_team': False, 'default_consume_items': False, 'default_autoclaim_rewards': 'disabled',
        'default_quest_shape': pack.get('default_shape', 'circle'), 'default_quest_disable_jei': False,
        'detection_delay': 20, 'disable_gui': False, 'drop_loot_crates': False, 'emergency_items_cooldown': 300,
        'grid_scale': D(0.5), 'lock_message': '', 'pause_game': False, 'progression_mode': 'linear',
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

    if os.path.isdir(GROUPS_DIR):
        shutil.rmtree(GROUPS_DIR)
    for key, members in sorted(STRUCTURE_GROUPS.items()):
        write(os.path.join(GROUPS_DIR, key + '.json'), json.dumps({'replace': False, 'values': members}, indent=2) + '\n')

    note = '// Generated by tools/quests/make_quests.py from tools/quests/src. Do not edit; edit the sources and rerun.\n'
    items = sorted(ctx['quest_items'].values(), key=lambda i: i['id'])
    write(ITEMS_JS, note + '// Quest items: letters, notes and keepsakes that start quests (see quest_givers.js).\n'
          'StartupEvents.registry(\'item\', event => {\n' + ''.join(
              f"  event.create({json.dumps(i['id'])}).displayName({json.dumps(i['name'])}).texture({json.dumps(i['texture'])})"
              f".maxStackSize(1).tooltip({json.dumps(i['tooltip'])})" + ('.glow(true)' if i['glow'] else '') + '\n'
              for i in items) + '})\n')
    write(GIVERS_JS, '// priority: 100\n' + note +
          '// Who gives which quest. Read by quest_givers.js.\n'
          'global.QUEST_GIVERS = ' + json.dumps(givers, indent=2) + '\n'
          'global.QUEST_CHARACTERS = ' + json.dumps(characters, indent=2) + '\n'
          'global.QUEST_ORGS = ' + json.dumps(orgs, indent=2) + '\n'
          '// Puzzle blocks that can\'t be broken, blown up or pushed inside these structures (fotfskills QuestProtect).\n'
          'global.QUEST_PROTECT = ' + json.dumps(ctx['protect'], indent=2) + '\n'
          '// Protected areas around the quest characters (src/npc_positions.json): no breaking or placing (fotfskills QuestAreas).\n'
          'global.QUEST_AREAS = ' + json.dumps(npc_areas(), indent=2) + '\n')
    print('wrote ' + summary)


# protected box around each placed character: this far out sideways, below and above their feet
AREA_SIDE, AREA_BELOW, AREA_ABOVE = 12, 6, 16


def npc_areas():
    """Boxes around every character in src/npc_positions.json (overworld unless it says), so their homes can't be broken."""
    path = os.path.join(SRC, 'npc_positions.json')
    if not os.path.exists(path):
        return []
    out = []
    for cid, p in sorted(json.load(open(path, encoding='utf-8')).items()):
        if cid.startswith('_') or not isinstance(p, dict) or len(p.get('pos', [])) != 3:
            continue
        x, y, z = (int(v // 1) for v in p['pos'])
        out.append({'id': cid, 'dimension': p.get('dimension', 'minecraft:overworld'),
                    'min': [x - AREA_SIDE, y - AREA_BELOW, z - AREA_SIDE],
                    'max': [x + AREA_SIDE, y + AREA_ABOVE, z + AREA_SIDE]})
    return out


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(text)


if __name__ == '__main__':
    main()
