#!/usr/bin/env python3
"""Check the quest list (tools/quests/src/plans/quests/*.json) and report what it covers.

    python tools/quests/coverage.py            check, and write docs/quest-coverage.md
    python tools/quests/coverage.py --check    check only
    python tools/quests/coverage.py --gaps     also print the mods and landmarks without a quest

The quest list is the plan: every quest the pack will have, one line each, before it's written in full. Each file
is one questline:

    {"line": "Fishing path", "chapter": "skill_fishing", "group": "skills", "giver": "...", "feel": "...",
     "quests": [{"id": "first_cast", "title": "...", "tier": "prologue", "types": ["fetch"], "after": [],
                 "summary": "...", "mods": ["aquaculture"], "landmarks": ["#fishing_huts"],
                 "signature": "artifacts:anglers_hat", "reward": "..."}]}

"after" names quests in the same file by id, or in another file as "<file>:<id>". "mods" are keys of mods.json (or
any of a mod's ids). "landmarks" are "#group" (src/structure_groups.json), a structure id, or "feature:<id>"
(src/landmarks.json). The report is spoiler-free: counts and names of mods and landmarks, never quest content.
"""
import fnmatch
import glob
import json
import os
import sys
from collections import Counter, defaultdict

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
Q = os.path.join(ROOT, 'tools', 'quests')
TIERS = ['start', 'prologue', 'act1', 'act2', 'act3', 'act4', 'act5', 'post', 'any']
TYPES = {'fetch', 'collect', 'craft', 'build', 'kill', 'hunt', 'boss', 'drop', 'explore', 'discover', 'talk', 'deliver',
         'escort', 'encounter', 'timed', 'cook', 'brew', 'farm', 'fish', 'tame', 'ride', 'travel', 'milestone', 'spell',
         'trade', 'rescue', 'defend', 'puzzle', 'contest', 'photo', 'stealth'}
EXEMPT_ROLES = {'library', 'performance', 'client', 'admin', 'loot'}


def load(name):
    return json.load(open(os.path.join(Q, name), encoding='utf-8'))


def main():
    mods, roles = load('mods.json'), load('src/mod_roles.json')
    structures, groups, lm = load('structures.json'), load('src/structure_groups.json'), load('src/landmarks.json')
    mods.pop('_about', None)
    groups = {k: v for k, v in groups.items() if not k.startswith('_')}
    alias = {i: key for key, m in mods.items() for i in [key, m['slug']] + m['mod_ids']}
    role_of = {m: r for r, ms in roles.items() if isinstance(ms, list) for m in ms}
    role_of.update({m: 'exempt' for m in roles.get('exempt', {})})
    features = lm.get('features', {})
    errors, quests = [], {}

    files = sorted(glob.glob(os.path.join(Q, 'src', 'plans', 'quests', '*.json')))
    for path in files:
        fname = os.path.basename(path)[:-5]
        try:
            line = json.load(open(path, encoding='utf-8'))
        except ValueError as e:
            errors.append(f'{fname}: not valid JSON ({e})')
            continue
        for q in line.get('quests', []):
            qid = f'{fname}:{q.get("id")}'
            if qid in quests:
                errors.append(f'{qid}: duplicate id')
            quests[qid] = dict(q, _file=fname, _line=line.get('line', fname), _group=line.get('group', ''))

    sigs = {}
    for qid, q in quests.items():
        if q.get('tier') not in TIERS:
            errors.append(f'{qid}: tier {q.get("tier")!r} should be one of {", ".join(TIERS)}')
        for t in q.get('types', []):
            if t not in TYPES:
                errors.append(f'{qid}: unknown type {t!r} (known: {", ".join(sorted(TYPES))})')
        for a in q.get('after', []):
            ref = a if ':' in a else f'{q["_file"]}:{a}'
            if ref not in quests:
                errors.append(f'{qid}: "after" names {a!r}, which isn\'t in the list')
        q['_mods'] = set()
        for m in q.get('mods', []):
            if m in alias:
                q['_mods'].add(alias[m])
            else:
                errors.append(f'{qid}: unknown mod {m!r} (use a key of tools/quests/mods.json)')
        for l in q.get('landmarks', []):
            if l.startswith('#'):
                ok = l[1:] in groups
            elif l.startswith('feature:'):
                ok = l[len('feature:'):] in features
            else:
                ok = l in structures and structures[l]['generates']
            if not ok:
                errors.append(f'{qid}: unknown or non-generating landmark {l!r}')
        s = q.get('signature')
        if s:
            if s in sigs:
                errors.append(f'{qid}: {s} is already the signature of {sigs[s]}')
            sigs[s] = qid

    for e in errors:
        print('error: ' + e)
    if errors:
        sys.exit(f'{len(errors)} problem(s)')

    # ---- coverage ----
    per_mod = Counter(m for q in quests.values() for m in q['_mods'])
    expected = {k: m for k, m in mods.items() if role_of.get(k) not in EXEMPT_ROLES and role_of.get(k) != 'exempt'}
    mods_missing = sorted((k for k in expected if not per_mod[k]), key=lambda k: mods[k]['name'].lower())

    scenery = lm.get('scenery', [])
    is_scenery = lambda sid: any(fnmatch.fnmatch(sid, p) for p in scenery)
    gen = {k for k, v in structures.items() if v['generates']}
    in_group = defaultdict(set)
    for g, members in groups.items():
        for sid in members:
            in_group[sid].add(g)
    units = {}   # landmark unit -> (label, dimension, mod)
    for g, members in groups.items():
        live = [s for s in members if s in gen and not is_scenery(s)]
        if live:
            dims = sorted({d for s in live for d in structures[s]['dimensions']})
            units['#' + g] = (f'{g.replace("_", " ").capitalize()} ({len(live)} kinds)', '/'.join(dims), 'several mods')
    for sid in sorted(gen):
        if sid in in_group or is_scenery(sid):
            continue
        v = structures[sid]
        units[sid] = (f'`{sid}`' + (f' ({v["name"]})' if v.get('name') else ''), '/'.join(v['dimensions']), v['mod'])
    for fid, f in features.items():
        units['feature:' + fid] = (f['name'], 'Overworld' if 'end' not in fid else 'End', f['mod'])
    covered = set()
    for q in quests.values():
        for l in q.get('landmarks', []):
            covered.add(l)
            for g in in_group.get(l, ()):
                covered.add('#' + g)
    lm_missing = [u for u in units if u not in covered]

    all_artifacts = sorted(i for i in load('registry.json')['items'] if i.startswith('artifacts:')
                           and i not in ('artifacts:mimic_spawn_egg',) and not i.startswith('artifacts:umbrella_'))
    lines_count = Counter(q['_line'] for q in quests.values())
    summary = (f'{len(quests)} quests in {len(files)} questlines; mods {len(expected) - len(mods_missing)}/{len(expected)}; '
               f'landmarks {len(units) - len(lm_missing)}/{len(units)}; artifacts {len(sigs)}/{len(all_artifacts)}')
    if '--gaps' in sys.argv:
        print('mods without a quest: ' + ', '.join(mods[k]['name'] for k in mods_missing))
        print('landmarks without a quest: ' + ', '.join(units[u][0] for u in lm_missing))
        print('artifacts without a quest: ' + ', '.join(a for a in all_artifacts if a not in sigs))
    if '--check' in sys.argv:
        print('ok: ' + summary)
        return

    out = ['# Quest coverage', '',
           'Generated by `tools/quests/coverage.py` from the quest list (`tools/quests/src/plans/quests/`, spoilers). '
           'Spoiler-free: counts, and the names of mods and landmarks, never what the quests are.', '',
           f'**{len(quests)} quests** in {len(files)} questlines. Mods: **{len(expected) - len(mods_missing)} of '
           f'{len(expected)}** that should appear do. Landmarks: **{len(units) - len(lm_missing)} of {len(units)}** have '
           f'a quest. Artifacts: **{len(sigs)} of {len(all_artifacts)}** have a quest built around them.', '',
           '## Questlines', '', '| Questline | Quests |', '|---|---|']
    out += [f'| {name} | {n} |' for name, n in sorted(lines_count.items())]
    tiers = Counter(q['tier'] for q in quests.values())
    out += ['', '## When in the game', '', '| Stage | Quests |', '|---|---|'] + [f'| {t} | {tiers[t]} |' for t in TIERS if tiers[t]]
    types = Counter(t for q in quests.values() for t in q.get('types', []))
    out += ['', '## Quest types', '', ', '.join(f'{t} {n}' for t, n in types.most_common()), '']
    out += ['## Mods', '', '| Mod | Quests |', '|---|---|']
    out += [f'| {mods[k]["name"]} | {per_mod[k] or "**none**"} |' for k in sorted(expected, key=lambda k: mods[k]['name'].lower())]
    exempt = sorted((k for k in mods if k not in expected), key=lambda k: mods[k]['name'].lower())
    out += ['', f'Not expected in quests ({len(exempt)}: libraries, performance, client-side, admin and loot mods): '
            + ', '.join(mods[k]['name'] for k in exempt), '']
    out += [f'## Landmarks without a quest ({len(lm_missing)} of {len(units)})', '',
            'Not every landmark needs one; this is the list to pick from. A family counts once (any member covers it). '
            'Scenery (trees, log piles, lanterns, rubble) is left out.', '', '| Landmark | Where | Mod |', '|---|---|---|']
    out += [f'| {units[u][0]} | {units[u][1]} | {units[u][2]} |'
            for u in sorted(lm_missing, key=lambda u: (units[u][1], units[u][2], units[u][0]))]
    out += ['', f'## Landmarks with a quest ({len(units) - len(lm_missing)})', '',
            ', '.join(units[u][0] for u in sorted(units) if u in covered), '']
    with open(os.path.join(ROOT, 'docs', 'quest-coverage.md'), 'w', encoding='utf-8', newline='\n') as fh:
        fh.write('\n'.join(out))
    print('wrote docs/quest-coverage.md: ' + summary)


if __name__ == '__main__':
    main()
