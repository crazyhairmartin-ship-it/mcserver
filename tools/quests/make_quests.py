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
            'advancements': 'advancement', 'dimensions': 'dimension', 'textures': 'texture'}
SHAPES = {'circle', 'square', 'rsquare', 'diamond', 'pentagon', 'hexagon', 'octagon', 'heart', 'gear'}


# ---- SNBT ----

class D(float):
    """A double (written 1.0d)."""


class F(float):
    """A float (written 0.5f)."""


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
    if isinstance(value, F):
        return f'{float(value)!r}f'
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


def trophy_target(tasks):
    """The creature a hunt is about: the last single target in the quest (a boss, a named spawn of one, a kill of
    one, or a named kill encounter). Quests like that get its trophy (Dylan, 2026-10-15)."""
    found = None
    for t in tasks:
        if not isinstance(t, dict):
            continue
        if isinstance(t.get('kill'), str):
            sp = t.get('spawn') if isinstance(t.get('spawn'), dict) else {}
            if sp.get('ensure') or (sp.get('name') and sp.get('wave', 4) == 1) or int(t.get('count', 1)) == 1:
                found = t['kill']
        e = t.get('encounter')
        if isinstance(e, dict) and e.get('then') == 'kill' and e.get('entity') and e.get('name'):
            found = e['entity']
    return found


def table_entries(name, rewards, reg, where, problems):
    """Reward table entries from [{"item": ..., "count", "weight", plus name/lore/enchant/unbreakable}]."""
    entries = []
    for n, e in enumerate(rewards):
        if not isinstance(e, dict) or 'item' not in e:
            problems.error(where, f'reward {n + 1} in the table needs an "item"')
            continue
        if isinstance(e.get('item'), str) and e['item'].split(':')[0] in SIGNATURE_MODS \
                and e['item'] not in SIGNATURE_EXEMPT:
            problems.warn(where, f'{e["item"]} in a reward table: artifacts should come from the quest built '
                                 'around them')
        entry = {'id': fid('table', name, str(n)), 'type': 'item', 'item': item_value(e, reg, where, problems)}
        if e.get('count', 1) != 1:
            entry['count'] = e['count']
        if e.get('weight', 1) != 1:
            entry['weight'] = float(e['weight'])
        entries.append(entry)
    return entries


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
    elif 'trophy' in r:
        # Jonn's Trophies: a little statue of the mob on a stand (size and base from the mod's config)
        ent = r['trophy']
        reg.check('entities', ent, where, r.get('unchecked', False))
        if not isinstance(ent, str) or ':' not in ent:
            return None
        ns, path = ent.split(':', 1)
        # every field set: a trophy without BaseBlock crashes chunk saving (seen on the test server, 2026-10-15).
        # Players can resize it by right-clicking it once placed.
        reward.update(type='item', item={'id': 'trophymanager:trophy', 'Count': B(1), 'tag': {
            'TrophyType': 'entity', 'TrophyEntity': {'entityType': ent}, 'Name': f'entity.{ns}.{path}',
            'BaseBlock': 'minecraft:smooth_stone_slab', 'Scale': F(0.5), 'OffsetY': D(0.5), 'RotX': F(0.0)}})
    elif 'choice' in r and isinstance(r['choice'], list):
        # the player picks one of these: the generator makes a reward table for the quest
        name = 'choice_' + '_'.join(ids).lower()
        entries = table_entries(name, r['choice'], reg, where, problems)
        if len(entries) < 2:
            problems.error(where, 'a choice reward needs at least two options')
            return None
        tid = fid('table', name)
        ctx['tables'][name] = tid
        ctx['tables_out'][name] = {'id': tid, 'title': r.get('title', 'Choose one'), 'icon': 'minecraft:chest',
                                   'loot_size': 1, 'order_index': len(ctx['tables_out']), 'use_title': True,
                                   'rewards': entries}
        reward.update(type='choice', table_id=L(int(tid, 16)))
    elif 'choice' in r:
        # the player picks one reward from a table in src/reward_tables (e.g. the main story's relics)
        if r['choice'] not in ctx['tables']:
            problems.error(where, f'unknown reward table {r["choice"]!r} (tools/quests/src/reward_tables/)')
            return None
        reward.update(type='choice', table_id=L(int(ctx['tables'][r['choice']], 16)))
    elif 'command' in r:
        reward.update(type='command', command=r['command'], elevate_perms=True, silent=r.get('silent', True))
        if 'title' not in r:
            problems.warn(where, 'command rewards should have a "title" so players know what they get')
    elif 'stage' in r:
        reward.update(type='gamestage', stage=r['stage'])
    else:
        problems.error(where, f'unknown reward {json.dumps(r)}; use item, skill, xp, levels, table, choice, command '
                              'or stage')
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
             'distance': spec.get('distance', [24, 40] if then == 'kill' else [8, 16]),
             'minutes': float(spec.get('minutes', 20)), 'boost': build_boost(spec, then == 'kill', where, problems),
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
TIMED_BANS = ('teleport', 'mounts', 'elytra', 'pearls', 'hurt', 'ground', 'seen')  # never grappling hooks: Dylan wants them allowed
# where a course's checkpoints go, and their usual spacing and size
COURSE_DEFAULTS = {'water': {'spread': [20, 45], 'radius': 5}, 'ground': {'spread': [15, 35], 'radius': 4},
                   'roofs': {'spread': [6, 16], 'radius': 2.5}, 'air': {'spread': [30, 70], 'radius': 7}}


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
    elif 'course' in goal:
        c = goal['course'] if isinstance(goal['course'], dict) else {}
        on = c.get('on', 'ground')
        if on not in COURSE_DEFAULTS:
            problems.error(where, f'course "on" must be one of {", ".join(COURSE_DEFAULTS)}')
            return None, None
        d = COURSE_DEFAULTS[on]
        spread = c.get('spread', d['spread'])
        height = c.get('height', [6, 20])
        count = int(c.get('checkpoints', 5))
        if not (isinstance(spread, list) and len(spread) == 2 and 2 <= spread[0] <= spread[1] <= 200):
            problems.error(where, 'course "spread" must be [min, max] blocks between checkpoints, 2-200')
            return None, None
        if not 2 <= count <= 20:
            problems.error(where, 'course "checkpoints" must be 2-20')
        out_goal = {'kind': 'course', 'on': on, 'count': count, 'spread': [int(spread[0]), int(spread[1])],
                    'radius': float(c.get('radius', d['radius'])), 'loop': bool(c.get('loop', False)),
                    'height': [int(height[0]), int(height[1])]}
    elif 'legs' in goal:
        legs = []
        for n2, leg in enumerate(goal['legs'] if isinstance(goal['legs'], list) else []):
            dest = build_destination(leg, ctx['registry'], f'{where} > leg {n2 + 1}', problems)
            if dest:
                dest['away'] = int(leg.get('away', 0))
                legs.append(dest)
        if len(legs) < 2:
            problems.error(where, '"legs" needs at least two stops')
            return None, None
        out_goal = {'kind': 'legs', 'legs': legs}
    else:
        problems.error(where, 'timed goal must be "kill", "stat", "place", "structure", "hold", "course" or "legs"')
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
    start_in = None
    if 'start_in' in spec:
        start_in = build_destination(spec['start_in'], ctx['registry'], where + ' > start_in', problems)
    entry = {'quest': f'{chapter}:{qid}', 'stage': f'{giver_stage(chapter, qid)}.timed{n}', 'type': 'timed',
             'seconds': seconds, 'goal': out_goal, 'start_in': start_in, 'no': [b for b in banned if b in TIMED_BANS], 'waves': waves, 'lines': spec.get('lines', []), 'start': spec.get('start', 'Start'),
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
    {"waystones": 3, "wild": true} counts only waystones found in the wild (not villages or player-made);
    "total": true counts every waystone they have, old ones too (milestones)."""
    count = int(t['waystones'])
    if count < 1:
        problems.error(where, '"waystones" needs a count of 1 or more')
    entry = {'quest': f'{chapter}:{qid}', 'stage': f'{giver_stage(chapter, qid)}.waystones{n}', 'type': 'waystones',
             'count': count, 'wild': bool(t.get('wild', False)), 'total': bool(t.get('total', False)),
             'requires': [], 'quest_id': quest_id,
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


SPELL_SCHOOLS = ('fire', 'ice', 'lightning', 'holy', 'ender', 'blood', 'evocation', 'nature', 'eldritch', 'any')


def build_spellkill(t, chapter, qid, n, quest_id, prev_tasks, ctx, where, problems):
    """A "spellkill" task (Iron's Spells): kill mobs with a school's magic while the step is open, the spell landing
    the killing blow. {"spellkill": ["minecraft:zombie", "minecraft:skeleton"], "school": "fire", "count": 12}
    ("any" for any mob or any school)."""
    mobs = t['spellkill']
    mobs = [] if mobs == 'any' else (mobs if isinstance(mobs, list) else [mobs])
    for m in mobs:
        ctx['registry'].check('entities', m, where, t.get('unchecked', False))
    school = t.get('school', 'any')
    if school not in SPELL_SCHOOLS:
        problems.error(where, f'spellkill "school" must be one of {", ".join(SPELL_SCHOOLS)}')
    count = int(t.get('count', 1))
    entry = {'quest': f'{chapter}:{qid}', 'stage': f'{giver_stage(chapter, qid)}.spellkill{n}', 'type': 'spellkill',
             'entities': mobs, 'school': school, 'count': count, 'requires': [], 'quest_id': quest_id,
             'prev_tasks': list(prev_tasks)}
    task = {'id': fid('task', chapter, qid, str(n)), 'type': 'gamestage', 'stage': entry['stage'],
            'title': t.get('title', f'Defeat {count} with {"magic" if school == "any" else school + " magic"}')}
    return task, entry


# named quest targets (kill encounters) are tougher and bigger than wild ones; spawn waves are normal unless they ask
# (Dylan, 2026-10-14). "boost" on an encounter or spawn overrides: {"health": 2, "damage": 1.5, "speed": 1.0, "scale": 1.25}, or false for none
BOOST_QUARRY = {'health': 2.0, 'damage': 1.5, 'speed': 1.0, 'scale': 1.25}
BOOST_WAVE = {'health': 1.5, 'damage': 1.25, 'speed': 1.0, 'scale': [1.0, 1.2]}


def build_boost(spec, default_on, where, problems, wave=False):
    b = spec.get('boost', None)
    if b is False or (b is None and not default_on):
        return None
    out = dict(BOOST_WAVE if wave else BOOST_QUARRY)
    if isinstance(b, dict):
        for k, v in b.items():
            if k not in out:
                problems.error(where, f'"boost" takes health, damage, speed and scale, not {k!r}')
            out[k] = v
    return out


def build_spawn(t, chapter, qid, n, quest_id, prev_tasks, ctx, where, problems):
    """A kill task's "spawn": when the player reaches "at" while the step is open, the enemies spawn around them in
    waves of "wave" (default up to 6) until the kill count is done; leftovers vanish when they leave. "ensure": true
    (bosses) only spawns when none of that mob is within 64 blocks, so the structure's own boss is fought if it's there.
    {"kill": "minecraft:zombie", "count": 8, "spawn": {"at": {"structure": "#graveyards"}, "wave": 4,
     "name": "Restless Dead", "health": 30, "glow": false}}"""
    spec = t['spawn']
    if not isinstance(spec, dict) or 'at' not in spec:
        problems.error(where, '"spawn" needs "at": {"place": id} or {"structure": id}')
        return None
    at = build_destination(spec['at'], ctx['registry'], where, problems)
    if not at:
        return None
    count = int(t.get('count', 1))
    entry = {'quest': f'{chapter}:{qid}', 'stage': f'{giver_stage(chapter, qid)}.spawn{n}', 'type': 'spawn',
             'entity': t['kill'], 'at': at, 'wave': int(spec.get('wave', min(count, 6))), 'name': spec.get('name', ''),
             'health': spec.get('health'), 'glow': bool(spec.get('glow', False)), 'ensure': bool(spec.get('ensure', False)),
             'boost': build_boost(spec, False, where, problems, wave=True),
             'task_id': fid('task', chapter, qid, str(n)), 'requires': [], 'quest_id': quest_id,
             'prev_tasks': list(prev_tasks)}
    return entry


def build_mine(t, chapter, qid, n, quest_id, prev_tasks, ctx, where, problems):
    """A "mine" task: break that many blocks (any, an id, "#tag", or a list) while the step is open; Ultimine counts.
    {"mine": "any", "count": 1000} or {"mine": "gravestone:gravestone"}."""
    keys = t['mine']
    keys = [] if keys == 'any' else (keys if isinstance(keys, list) else [keys])
    for k in keys:
        if not k.startswith('#'):
            ctx['registry'].check('items', k, where, t.get('unchecked', False))
    count = int(t.get('count', 1))
    entry = {'quest': f'{chapter}:{qid}', 'stage': f'{giver_stage(chapter, qid)}.mine{n}', 'type': 'mine', 'keys': keys,
             'count': count, 'requires': [], 'quest_id': quest_id, 'prev_tasks': list(prev_tasks)}
    task = {'id': fid('task', chapter, qid, str(n)), 'type': 'gamestage', 'stage': entry['stage'],
            'title': t.get('title', f'Mine {count} blocks')}
    return task, entry


def build_skill_level(t, chapter, qid, n, quest_id, prev_tasks, ctx, where, problems):
    """A "skill_level" task: reach that level in a Pufferfish skill tree ("tree": a tree like "mining", or "any")."""
    level = int(t['skill_level'])
    tree = t.get('tree', 'any')
    if tree != 'any' and tree not in ctx['skills']:
        problems.error(where, f'unknown skill tree {tree!r} (one of {", ".join(sorted(ctx["skills"]))}, or "any")')
    entry = {'quest': f'{chapter}:{qid}', 'stage': f'{giver_stage(chapter, qid)}.skill{n}', 'type': 'skill_level',
             'level': level, 'tree': tree, 'spent': bool(t.get('spent', False)), 'requires': [], 'quest_id': quest_id, 'prev_tasks': list(prev_tasks)}
    what = 'a skill' if tree == 'any' else ctx['skills'][tree][0]
    task = {'id': fid('task', chapter, qid, str(n)), 'type': 'gamestage', 'stage': entry['stage'],
            'title': t.get('title', f'Reach level {level} in {what}')}
    return task, entry


def build_stats(t, chapter, qid, n, quest_id, prev_tasks, ctx, where, problems):
    """A "stats" task: the lifetime sum of several vanilla statistics reaches "count" (milestones, e.g. distance
    travelled on foot: walk + sprint + crouch + swim)."""
    stats = t['stats']
    if not isinstance(stats, list) or not stats or not all(':' in x for x in stats):
        problems.error(where, '"stats" needs a list of namespaced statistics, like minecraft:walk_one_cm')
        return None, None
    entry = {'quest': f'{chapter}:{qid}', 'stage': f'{giver_stage(chapter, qid)}.stats{n}', 'type': 'stats',
             'stats': stats, 'count': int(t.get('count', 1)), 'requires': [], 'quest_id': quest_id,
             'prev_tasks': list(prev_tasks)}
    task = {'id': fid('task', chapter, qid, str(n)), 'type': 'gamestage', 'stage': entry['stage'],
            'title': t.get('title', 'Reach the milestone')}
    return task, entry


def build_use(t, chapter, qid, n, quest_id, prev_tasks, ctx, where, problems):
    """A "use" task: right-click "count" different blocks of that kind (id, "#tag" or list) while the step is open.
    Optional "at" (only inside that place/structure), "within" seconds (all of them inside that window: ring both bells
    within a minute), "holding" an item (an offering) and "consume" (it's used up). Build puzzles on blocks the
    structure really has: tools/quests/src/structure_contents.json."""
    keys = t['use']
    keys = keys if isinstance(keys, list) else [keys]
    for k in keys:
        if not k.startswith('#'):
            ctx['registry'].check('items', k, where, t.get('unchecked', False))
    at = build_destination(t['at'], ctx['registry'], where, problems) if 'at' in t else None
    holding = t.get('holding', '')
    if holding:
        ctx['registry'].check('items', holding, where)
    count = int(t.get('count', 1))
    entry = {'quest': f'{chapter}:{qid}', 'stage': f'{giver_stage(chapter, qid)}.use{n}', 'type': 'use', 'keys': keys,
             'count': count, 'at': at, 'within': int(t.get('within', 0)), 'holding': holding,
             'consume': bool(t.get('consume', False)), 'requires': [], 'quest_id': quest_id,
             'prev_tasks': list(prev_tasks)}
    name = keys[0].lstrip('#').split(':')[-1].replace('_', ' ')
    task = {'id': fid('task', chapter, qid, str(n)), 'type': 'gamestage', 'stage': entry['stage'],
            'title': t.get('title', f'Use {count} {name}{"s" if count > 1 else ""}')}
    return task, entry


def build_search(t, chapter, qid, n, quest_id, prev_tasks, ctx, where, problems):
    """A "search" task: open the containers (chests, barrels, pots, Lootr chests...) inside "at" and the quest's item
    turns up in "count" different ones, straight into the player's pack. {"search": {"at": {"structure": id},
    "count": 4, "item": {"name": "Portrait Key", "texture": "minecraft:block/tripwire_hook"},
    "found": "Behind a loose board you find a key."}}. The items are the step: carrying "count" of them completes it."""
    spec = t['search']
    if not isinstance(spec, dict) or 'at' not in spec or not isinstance(spec.get('item'), dict):
        problems.error(where, '"search" needs "at" and "item": {"name": ...}')
        return None, None
    at = build_destination(spec['at'], ctx['registry'], where, problems)
    if not at:
        return None, None
    it = dict(spec['item'])
    it.setdefault('tooltip', 'Quest item')
    item_id = quest_item_id({'item': it}, chapter, f'{qid}_{n}', ctx, where, problems)
    if not item_id:
        return None, None
    count = int(spec.get('count', 1))
    entry = {'quest': f'{chapter}:{qid}', 'stage': f'{giver_stage(chapter, qid)}.search{n}', 'type': 'search',
             'at': at, 'count': count, 'item': item_id, 'found': spec.get('found', ''), 'requires': [],
             'quest_id': quest_id, 'prev_tasks': list(prev_tasks)}
    task = {'id': fid('task', chapter, qid, str(n)), 'type': 'item', 'item': item_id,
            'title': t.get('title', f'Search for {it["name"]}')}
    if count != 1:
        task['count'] = L(count)
    return task, entry


def build_be(t, chapter, qid, n, quest_id, prev_tasks, ctx, where, problems):
    """A "be" task: the player stands somewhere that matches every condition given (checked every 5 seconds):
    {"be": {"biomes": [...], "dimension": id, "above_y": 192, "below_y": 0, "in_water": true, "sky": true,
    "night": true, "raining": true, "thundering": true, "time": [12000, 13000], "riding": "minecraft:horse"}}
    ("sky": open sky above them; "night": after dusk, before dawn; "time": day-time ticks from, to, e.g. sunset
    12000-13000, sunrise 23000-24000; "riding": on that mob, or a list)."""
    spec = t['be']
    if not isinstance(spec, dict) or not spec:
        problems.error(where, '"be" needs conditions: biomes, dimension, above_y, below_y, in_water, sky')
        return None, None
    for b in spec.get('biomes', []):
        ctx['registry'].check('biomes', b, where, t.get('unchecked', False))
    if spec.get('dimension'):
        ctx['registry'].check('dimensions', spec['dimension'], where)
    cond = {k: spec[k] for k in ('biomes', 'dimension', 'above_y', 'below_y', 'in_water', 'sky', 'night', 'raining',
                                 'thundering', 'time', 'riding') if k in spec}
    if 'riding' in spec:
        for r in (spec['riding'] if isinstance(spec['riding'], list) else [spec['riding']]):
            ctx['registry'].check('entities', r, where, t.get('unchecked', False))
    entry = {'quest': f'{chapter}:{qid}', 'stage': f'{giver_stage(chapter, qid)}.be{n}', 'type': 'be', 'where': cond,
             'requires': [], 'quest_id': quest_id, 'prev_tasks': list(prev_tasks)}
    task = {'id': fid('task', chapter, qid, str(n)), 'type': 'gamestage', 'stage': entry['stage'],
            'title': t.get('title', 'Get there')}
    return task, entry


def build_biomes(t, chapter, qid, n, quest_id, prev_tasks, ctx, where, problems):
    """A "biomes" task: visit that many different biomes (any dimension) while the step is open.
    {"biomes": 20} or {"biomes": 10, "dimension": "minecraft:overworld"}."""
    count = int(t['biomes'])
    if t.get('dimension'):
        ctx['registry'].check('dimensions', t['dimension'], where)
    entry = {'quest': f'{chapter}:{qid}', 'stage': f'{giver_stage(chapter, qid)}.biomes{n}', 'type': 'biomes',
             'count': count, 'dimension': t.get('dimension', ''), 'requires': [], 'quest_id': quest_id,
             'prev_tasks': list(prev_tasks)}
    task = {'id': fid('task', chapter, qid, str(n)), 'type': 'gamestage', 'stage': entry['stage'],
            'title': t.get('title', f'Visit {count} different biomes')}
    return task, entry


def ids_list(value):
    return [] if value in (None, 'any') else (value if isinstance(value, list) else [value])


EVENT_TASKS = ('make', 'trade', 'sleep', 'interact', 'have', 'visits', 'killwith')


def build_event_task(t, kind, chapter, qid, n, quest_id, prev_tasks, ctx, where, problems):
    """Tasks counted from game events while the step is open:
    make:     {"make": "minecraft:cake" (or list), "count": 3, "how": "craft"|"smelt"|"brew"|"any"}  items made
    trade:    {"trade": "any" | villager profession | mob id, "item": result id (optional), "count": 2}  trades done
    sleep:    {"sleep": 1}  nights slept through (waking in the morning)
    interact: {"interact": mob id (or list), "holding": item id, "consume": true, "count": 2}  right-click that many
              different mobs of that kind holding the item (give a collar, feed, saddle, name...)
    have:     {"have": item id, "count": 1, "enchant": {id: min level}, "potion": "minecraft:fire_resistance",
              "consume": false}  carrying items with those details (an enchanted book with both, a specific potion)
    visits:   {"visits": structure id / "#group" / list, "count": 3, "apart": 150, "label": "a well"}  being inside
              that many different ones (each at least "apart" blocks from the others)
    killwith: {"killwith": mob id / list / "any", "with": item id / "#tag" / list, "count": 6}  kills where the
              weapon in hand, or the thrown thing that hit, matches (a thrown spear's entity id counts too)"""
    reg = ctx['registry']
    entry = {'quest': f'{chapter}:{qid}', 'stage': f'{giver_stage(chapter, qid)}.{kind}{n}', 'type': kind,
             'count': int(t.get('count', 1)), 'requires': [], 'quest_id': quest_id, 'prev_tasks': list(prev_tasks)}
    if kind == 'make':
        items = ids_list(t['make'])
        for i in items:
            reg.check('items', i, where, t.get('unchecked', False))
        how = t.get('how', 'any')
        if how not in ('craft', 'smelt', 'brew', 'any'):
            problems.error(where, '"how" must be craft, smelt, brew or any')
        entry.update(items=items, how=how)
        default = 'Make it'
    elif kind == 'trade':
        entry.update(who=t['trade'], item=t.get('item', ''))
        if t.get('item'):
            reg.check('items', t['item'], where, t.get('unchecked', False))
        default = 'Make a trade'
    elif kind == 'sleep':
        entry['count'] = int(t['sleep'])
        default = 'Sleep through the night'
    elif kind == 'have':
        reg.check('items', t['have'], where, t.get('unchecked', False))
        enchants = t.get('enchant', {})
        for e in enchants:
            reg.check('enchantments', e, where, t.get('unchecked', False))
        entry.update(item=t['have'], enchant={k: int(v) for k, v in enchants.items()}, potion=t.get('potion', ''),
                     consume=bool(t.get('consume', False)))
        default = 'Have it with you'
    elif kind == 'visits':
        structures = expand_structures(t['visits'], reg, where, problems)
        if not structures:
            problems.error(where, '"visits" needs a structure id, "#group" or a list')
        apart = int(t.get('apart', 150))
        if apart < 32:
            problems.error(where, '"apart" must be at least 32 blocks (one structure can be big)')
        entry.update(structures=structures, apart=apart, label=t.get('label', 'one'))
        default = f'Visit {entry["count"]} different places'
    elif kind == 'killwith':
        mobs = [] if t['killwith'] == 'any' else ids_list(t['killwith'])
        for m in mobs:
            reg.check('entities', m, where, t.get('unchecked', False))
        weapons = ids_list(t.get('with'))
        if not weapons:
            problems.error(where, '"killwith" needs "with": an item id, "#tag" or entity id, or a list')
        entry.update(entities=mobs, weapons=weapons)
        default = 'Defeat them'
    else:
        mobs = ids_list(t['interact'])
        for m in mobs:
            reg.check('entities', m, where, t.get('unchecked', False))
        holding = t.get('holding', '')
        if holding:
            reg.check('items', holding, where, t.get('unchecked', False))
        entry.update(entities=mobs, holding=holding, consume=bool(t.get('consume', False)))
        default = 'Do it'
    task = {'id': fid('task', chapter, qid, str(n)), 'type': 'gamestage', 'stage': entry['stage'],
            'title': t.get('title', default)}
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
    if 'texture' in spec:
        # block items and banners have no item/<name> texture: a wrong path shows pink and black in game
        ctx['registry'].check('textures', spec['texture'], where)
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
    ctx['tables_out'] = tables_out   # choice rewards listed in a quest add their tables here
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
        entries = table_entries(name, t.get('rewards', []), reg, where, problems)
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
                elif isinstance(t, dict) and 'spellkill' in t:
                    task, entry = build_spellkill(t, name, qid, n, quest['id'], [x['id'] for x in tasks], ctx, twhere,
                                                  problems)
                    if entry:
                        givers.append(entry)
                elif isinstance(t, dict) and 'cast' in t:
                    task, entry = build_cast(t, name, qid, n, quest['id'], [x['id'] for x in tasks], ctx, twhere,
                                             problems)
                    if entry:
                        givers.append(entry)
                elif isinstance(t, dict) and any(k in t for k in EVENT_TASKS):
                    kind = next(k for k in EVENT_TASKS if k in t)
                    task, entry = build_event_task(t, kind, name, qid, n, quest['id'], [x['id'] for x in tasks], ctx,
                                                   twhere, problems)
                    if entry:
                        givers.append(entry)
                elif isinstance(t, dict) and ('be' in t or (isinstance(t.get('biomes'), int))):
                    builder = build_be if 'be' in t else build_biomes
                    task, entry = builder(t, name, qid, n, quest['id'], [x['id'] for x in tasks], ctx, twhere, problems)
                    if entry:
                        givers.append(entry)
                elif isinstance(t, dict) and ('use' in t or 'search' in t):
                    builder = build_use if 'use' in t else build_search
                    task, entry = builder(t, name, qid, n, quest['id'], [x['id'] for x in tasks], ctx, twhere, problems)
                    if entry:
                        givers.append(entry)
                elif isinstance(t, dict) and ('mine' in t or 'skill_level' in t or 'stats' in t):
                    builder = build_mine if 'mine' in t else build_skill_level if 'skill_level' in t else build_stats
                    task, entry = builder(t, name, qid, n, quest['id'], [x['id'] for x in tasks], ctx, twhere, problems)
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
                    if isinstance(t, dict) and 'kill' in t and 'spawn' in t:
                        entry = build_spawn(t, name, qid, n, quest['id'], [x['id'] for x in tasks], ctx, twhere,
                                            problems)
                        if entry:
                            givers.append(entry)
                        t = {k: v for k, v in t.items() if k != 'spawn'}
                    task = build_task(t, ('task', name, qid, str(n)), reg, twhere, problems)
                if task:
                    tasks.append(task)
            if not tasks:
                problems.error(where, 'a quest needs at least one task')
            quest['tasks'] = tasks
            rewards = []
            src_rewards = list(q.get('rewards', []))
            if q.get('trophy', True) is not False \
                    and not any(isinstance(r, dict) and 'trophy' in r for r in src_rewards):
                target = q['trophy'] if isinstance(q.get('trophy'), str) else trophy_target(q.get('tasks', []))
                if target:
                    src_rewards.append({'trophy': target})
            for n, r in enumerate(src_rewards):
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
