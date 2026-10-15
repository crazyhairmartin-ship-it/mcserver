"""Checks written quests for the problems reviews keep finding. Run it before committing quest work.

    python tools/quests/lint_quests.py [chapter ...]     (all chapters if none given)

Reads tools/quests/src/chapters/*.json. Errors (exit code 1) must be fixed; warnings must be fixed or, when the engine
truly can't do it, logged in src/plans/followups.md. What it checks:
  - checkmark tasks (the player just ticks a box): use a real task (see tools/quests/README.md)
  - plain "stat" tasks outside milestones: they read lifetime totals and complete at once; use a timed goal
  - generic lifetime advancements (tame/breed/enchant an item...) outside milestones: use tame/breed/use/cast tasks
  - timed runs measured with a distance stat: make them a structure/place goal with "away"
  - a kill step in a quest that sends the player to a place, without "spawn"
  - "use" and "search" at a structure that src/structure_contents.json says it doesn't have (or rarely has)
  - hostile spawns or spawn waves in villages (they kill villagers)
  - count steps (kill, use, search, cast, spellkill, tame, breed, mine, build) without an in-world "title"
  - quests without story text
  - generous item rewards (Dylan, 2026-10-15): more than one tool/weapon/armour piece is an error, more than three
    different items a warning (stacks of one item are fine)
  - dialogue over the limits (Dylan and Fionah, 2026-10-15): more than 2 lines in a conversation is an error, a line
    over 15 words a warning; character idle/hail lines in pack.json too
"""
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'src')
LIFETIME_ADV = ('husbandry/tame_an_animal', 'husbandry/breed_an_animal', 'story/enchant_item', 'adventure/kill_a_mob',
                'husbandry/fishy_business', 'story/mine_stone', 'story/smelt_iron')
DISTANCE_STATS = ('walk_one_cm', 'sprint_one_cm', 'swim_one_cm', 'boat_one_cm', 'horse_one_cm', 'aviate_one_cm')
TITLED = ('kill', 'use', 'search', 'cast', 'spellkill', 'tame', 'breed', 'mine', 'build')
# spawns that don't threaten villagers
PASSIVE = ('minecraft:cow', 'minecraft:pig', 'minecraft:sheep', 'minecraft:chicken', 'minecraft:rabbit', 'naturalist:boar',
           'naturalist:deer', 'minecraft:fox', 'minecraft:goat')


def load(name):
    with open(os.path.join(SRC, name), encoding='utf-8') as fh:
        return json.load(fh)


def main():
    contents = load('structure_contents.json')
    groups = {k: (v.get('structures') if isinstance(v, dict) else v)
              for k, v in load('structure_groups.json').items() if not k.startswith('_')}
    villages = set(groups.get('villages', []))
    wanted = set(sys.argv[1:])
    errors, warnings = [], []
    # quests already logged as needing the engine: their stand-ins are known, so they warn instead of failing
    fpath = os.path.join(SRC, 'plans', 'followups.md')
    logged = set()
    if os.path.exists(fpath):
        for line in open(fpath, encoding='utf-8'):
            if line.startswith('- ') and ':' in line:
                logged.add(':'.join(line[2:].split(':')[:2]).strip())

    def structures(ref):
        refs = ref if isinstance(ref, list) else [ref]
        out = []
        for r in refs:
            if isinstance(r, str) and r.startswith('#') and ':' not in r:
                out += groups.get(r[1:], [])
            elif isinstance(r, str) and not r.startswith('#'):
                out.append(r)
        return out

    def block_share(sid, key):
        """(pieces with the block, pieces) for an id key; None when unknown (tag, or not a jigsaw structure)."""
        c = contents.get(sid)
        if not c or not c.get('pieces') or key.startswith('#'):
            return None
        return c['blocks'].get(key, 0), c['pieces']

    def container_pieces(sid):
        c = contents.get(sid)
        if not c or not c.get('pieces'):
            return None
        return sum(n for b, n in c['blocks'].items() if any(w in b for w in ('chest', 'barrel', 'shulker', 'pot', 'crate'))), c['pieces']

    for path in sorted(glob.glob(os.path.join(SRC, 'chapters', '*.json'))):
        chapter = os.path.basename(path)[:-5]
        if wanted and chapter not in wanted:
            continue
        data = json.load(open(path, encoding='utf-8'))
        milestones = chapter == 'milestones'
        for q in data.get('quests', []):
            where = f'{chapter}:{q["id"]}'
            tasks = [t for t in q.get('tasks', []) if isinstance(t, dict)]
            gear = re.compile(r'(sword|pickaxe|_axe|shovel|_hoe|helmet|chestplate|leggings|boots|bow|crossbow|shield|'
                              r'spear|halberd|rapier|longsword|katana|glaive|mace|hammer|trident|scythe)$')
            items = [r['item'] for r in q.get('rewards', []) if isinstance(r, dict) and isinstance(r.get('item'), str)]
            if sum(1 for i in items if gear.search(i.split(':')[-1])) > 1:
                errors.append(f'{where}: more than one tool/weapon/armour piece as rewards (give one; stacks are fine)')
            if len(set(items)) > 3:
                warnings.append(f'{where}: {len(set(items))} different reward items (keep it to a few)')
            if not q.get('text'):
                warnings.append(f'{where}: no story text (every quest needs an in-world reason)')
            goes_somewhere = any('structure' in t or 'place' in t for t in tasks)
            convo = []
            if isinstance(q.get('giver'), dict) and q['giver'].get('lines'):
                convo.append(('giver', q['giver']['lines']))
            for n2, t in enumerate(tasks, 1):
                if t.get('lines'):
                    convo.append((f'task {n2}', t['lines']))
                for k in ('encounter', 'timed'):
                    if isinstance(t.get(k), dict):
                        for kk in ('lines', 'thanks'):
                            if t[k].get(kk):
                                convo.append((f'task {n2} {kk}', t[k][kk]))
            for label, lines in convo:
                if len(lines) > 2:
                    errors.append(f'{where} {label}: {len(lines)} lines of dialogue (at most 2 short ones)')
                for line in lines:
                    if len(line.split()) > 15:
                        warnings.append(f'{where} {label}: a {len(line.split())}-word line (keep lines under 15 words)')
            for n, t in enumerate(tasks, 1):
                w = f'{where} task {n}'
                if 'checkmark' in t:
                    (warnings if chapter == 'odd_jobs' or where in logged else errors).append(
                        f'{w}: checkmark "{t["checkmark"][:50]}" (use a real task, or log it in followups.md)')
                if 'stat' in t and not milestones:
                    errors.append(f'{w}: plain stat {t["stat"]} reads the lifetime total (make it a timed goal)')
                if 'advancement' in t and not milestones and any(a in t['advancement'] for a in LIFETIME_ADV):
                    errors.append(f'{w}: {t["advancement"]} is a lifetime advancement most players already have')
                timed = t.get('timed')
                if isinstance(timed, dict):
                    goal = timed.get('goal', {})
                    if isinstance(goal.get('stat'), str) and goal['stat'].split(':')[-1] in DISTANCE_STATS:
                        warnings.append(f'{w}: a run measured as a distance stat; make it a structure/place goal with "away"')
                if 'kill' in t and goes_somewhere and 'spawn' not in t:
                    warnings.append(f'{w}: kill at a place without "spawn" (the enemies may not be there)')
                spawn = t.get('spawn')
                if isinstance(spawn, dict) and t.get('kill') not in PASSIVE:
                    at = spawn.get('at', {})
                    if set(structures(at.get('structure', []))) & villages:
                        errors.append(f'{w}: hostile spawn in a village (they kill villagers)')
                if any(k in t for k in TITLED) and 'title' not in t:
                    warnings.append(f'{w}: no title (say what the step is in-world)')
                if 'use' in t and isinstance(t.get('at'), dict) and 'structure' in t['at']:
                    keys = t['use'] if isinstance(t['use'], list) else [t['use']]
                    for sid in structures(t['at']['structure']):
                        for k in keys:
                            share = block_share(sid, k)
                            if share is None:
                                continue
                            have, pieces = share
                            if have == 0:
                                errors.append(f'{w}: {sid} has no {k} (src/structure_contents.json)')
                            elif have * 5 < pieces:
                                warnings.append(f'{w}: {k} is in only {have} of {sid}\'s {pieces} pieces; it may not generate')
                if isinstance(t.get('search'), dict):
                    at = t['search'].get('at', {})
                    for sid in structures(at.get('structure', [])):
                        share = container_pieces(sid)
                        if share is not None and share[0] == 0:
                            errors.append(f'{w}: {sid} has no containers to search (src/structure_contents.json)')
    if not wanted or 'characters' in wanted:
        for cid, c in load('pack.json').get('characters', {}).items():
            if cid.startswith('_'):
                continue
            for kind in ('idle', 'hail'):
                for line in c.get(kind, []):
                    if len(line.split()) > 15:
                        warnings.append(f'character {cid} {kind}: a {len(line.split())}-word line (keep under 15 words)')
    # FTB reads "&" as a colour code: a plain one (not &0-9a-f/k-o/r) shows as "Invalid formatting!" in the book
    bad_amp = re.compile(r'&(?![0-9a-fk-orA-FK-OR])')
    for g in load('pack.json').get('groups', []):
        if bad_amp.search(g.get('title', '')):
            errors.append(f'group {g.get("id")}: "&" in its title (write "and")')
    for path in sorted(glob.glob(os.path.join(SRC, 'chapters', '*.json'))):
        text = open(path, encoding='utf-8').read()
        if bad_amp.search(text):
            errors.append(f'{os.path.basename(path)}: a plain "&" somewhere (FTB reads it as a colour code; write "and")')
    for e in errors:
        print('error: ' + e)
    for wn in warnings:
        print('warning: ' + wn)
    print(f'{len(errors)} error(s), {len(warnings)} warning(s)')
    sys.exit(1 if errors else 0)


if __name__ == '__main__':
    main()
