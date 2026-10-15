"""Check every quest puzzle against real generated structures on the test server.

    python tools/quests/verify_puzzles.py [--copies 3] [--chapters a,b] [--recheck]

Reads the generated quest data (kubejs/server_scripts/quest_givers.generated.js). For each "use" step at a structure
(right-click N of a block) and each "search" step (N containers), the structure's blocks are counted in real generated
copies (fotfskills /fotfverify). Writes tools/quests/src/plans/puzzle_check.md (spoilers): every step, the fewest any
copy had, and OK, SHORT or NOT FOUND. A SHORT step needs fixing: lower its count to what every copy has, switch it to
"search", or have the player bring the block ("build").

Results are remembered in src/plans/puzzle_cache.json per structure and block, so only new combinations are checked;
when everything is already known, no server is needed and it finishes at once. When something is new it starts the
test server itself (docker compose in ../server-test, at the pack's current commit), but only if nobody is on the live
server (starting it can disconnect players), and stops it again afterwards if it started it. --chapters limits the
report to those chapters; --recheck forgets the cache for them; --players-ok starts the test server even with players
on live (only when Dylan has said that's fine). Structures in a #group are checked through their first
three members.
"""
import argparse
import json
import os
import re
import subprocess
import time

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
GIVERS = os.path.join(ROOT, 'kubejs', 'server_scripts', 'quest_givers.generated.js')
OUT = os.path.join(ROOT, 'tools', 'quests', 'src', 'plans', 'puzzle_check.md')
CACHE = os.path.join(ROOT, 'tools', 'quests', 'src', 'plans', 'puzzle_cache.json')
TEST_DIR = os.path.join(os.path.dirname(ROOT), 'server-test')
LOG = os.path.join(TEST_DIR, 'data', 'logs', 'latest.log')
CONTAINER = 'fotf-test'
STRUCTURES = os.path.join(ROOT, 'tools', 'quests', 'structures.json')
DIMENSIONS = {'Overworld': 'minecraft:overworld', 'Nether': 'minecraft:the_nether', 'End': 'minecraft:the_end',
              'Twilight Forest': 'twilightforest:twilight_forest'}


def dimension_of(sid):
    """Where a structure generates (structures.json), so it's located in the right dimension."""
    try:
        dims = json.load(open(STRUCTURES, encoding='utf-8')).get(sid, {}).get('dimensions') or ['Overworld']
    except (OSError, ValueError):
        dims = ['Overworld']
    return DIMENSIONS.get(dims[0], 'minecraft:overworld')


def givers():
    text = open(GIVERS, encoding='utf-8').read()
    m = re.search(r'global\.QUEST_GIVERS = (\[.*?\n\])\n', text, re.S)
    return json.loads(m.group(1))


def sh(args, **kw):
    return subprocess.run(args, capture_output=True, text=True, **kw)


def test_running():
    return CONTAINER in sh(['docker', 'ps', '--format', '{{.Names}}']).stdout.split()


def live_players():
    out = sh(['docker', 'exec', 'server-mc-1', 'rcon-cli', 'list']).stdout
    m = re.search(r'There are (\d+)', out)
    return int(m.group(1)) if m else -1


def start_test():
    ref = sh(['git', '-C', ROOT, 'rev-parse', 'HEAD']).stdout.strip()
    sh(['docker', 'compose', 'up', '-d'], cwd=TEST_DIR, env=dict(os.environ, PACK_REF=ref))
    print(f'test server starting at {ref[:7]}...', flush=True)
    deadline = time.time() + 1200
    while time.time() < deadline:
        time.sleep(10)
        res = sh(['docker', 'logs', '--since', '20m', CONTAINER])
        logs = res.stdout + res.stderr
        if re.search(r'Done \([0-9.]+s\)! For help', logs):
            return True
        if 'Crash report' in logs or 'Exception in server tick loop' in logs:
            return False
    return False


def verify(sid, keys, copies):
    """Run /fotfverify and read its result lines from the test server's log (rcon replies can arrive late and get
    mixed up with the next command's while big structures generate)."""
    start = os.path.getsize(LOG) if os.path.exists(LOG) else 0
    cmd = f'execute in {dimension_of(sid)} run fotfverify "{sid}" {copies} {",".join(keys)}'
    subprocess.Popen(['docker', 'exec', CONTAINER, 'rcon-cli', '--', cmd],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    marker = 'fotfverify ' + sid + ' '
    deadline = time.time() + 1200
    while time.time() < deadline:
        time.sleep(3)
        with open(LOG, encoding='utf-8', errors='replace') as fh:
            fh.seek(start)
            new_text = fh.read()
        lines = [line[line.index(marker):] for line in new_text.splitlines() if marker in line]
        if any(' summary ' in line or ' unknown structure' in line for line in lines):
            return lines
    return []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--copies', type=int, default=3)
    ap.add_argument('--chapters', default='')
    ap.add_argument('--recheck', action='store_true')
    ap.add_argument('--players-ok', action='store_true', help='start the test server even with players on live (Dylan said so)')
    args = ap.parse_args()
    only = {c for c in args.chapters.split(',') if c}

    checks = []   # (quest, step kind, structure ids, keys, needed)
    all_givers = givers()
    # blocks a quest has the player place first (a "build" step) don't need to be in the structure already
    built = {(g['quest'], k) for g in all_givers if g['type'] == 'build' for k in g['keys']}
    for g in all_givers:
        at = g.get('at') or {}
        if at.get('kind') != 'structure' or (only and g['quest'].split(':')[0] not in only):
            continue
        sids = [s for s in at['structures'] if not s.startswith('#')][:3]
        if g['type'] == 'use' and not all((g['quest'], k) in built for k in g['keys']):
            checks.append((g['quest'], 'use', sids, g['keys'], g['count']))
        elif g['type'] == 'search':
            checks.append((g['quest'], 'search', sids, ['containers'], g['count']))

    cache = json.load(open(CACHE, encoding='utf-8')) if os.path.exists(CACHE) else {}
    needed = {}   # structure -> keys not yet known
    for _, _, sids, keys, _ in checks:
        for sid in sids:
            known = cache.get(sid, {}).get('mins', {})
            not_found = not cache.get(sid, {}).get('copies')
            for k in keys:
                if args.recheck or k not in known or not_found:
                    needed.setdefault(sid, set()).add(k)

    if needed:
        print(f'{sum(len(v) for v in needed.values())} new structure/block combinations to check', flush=True)
        started = False
        if not test_running():
            players = live_players()
            if players != 0 and not args.players_ok:
                print(f'not starting the test server: {players} player(s) on live (it can disconnect them). '
                      'Run this again when the live server is empty.')
                needed = {}
            elif start_test():
                started = True
            else:
                print('the test server did not start; nothing new was checked')
                needed = {}
        for sid, keys in sorted(needed.items()):
            print(f'checking {sid} ({", ".join(sorted(keys))})...', flush=True)
            lines = verify(sid, sorted(keys), args.copies)
            summary = next((l for l in lines if ' summary ' in l), '')
            found = int(re.search(r'copies=(\d+)', summary).group(1)) if summary else 0
            entry = cache.setdefault(sid, {'copies': 0, 'mins': {}, 'lines': []})
            entry['copies'] = max(entry['copies'], found)
            for k, v in re.findall(r'(\S+)_min=(\d+)', summary):
                entry['mins'][k] = int(v) if found else 0
            for k in keys:
                entry['mins'].setdefault(k, 0)
            entry['lines'] = sorted(set(entry['lines']) | {l for l in lines if ' copy ' in l})
            with open(CACHE, 'w', encoding='utf-8', newline='\n') as fh:
                json.dump(cache, fh, indent=1, sort_keys=True)
                fh.write('\n')
        if started:
            sh(['docker', 'compose', 'stop'], cwd=TEST_DIR)
            print('test server stopped', flush=True)

    rows, attention = [], []
    for quest, kind, sids, keys, need in checks:
        for sid in sids:
            entry = cache.get(sid)
            if not entry or any(k not in entry['mins'] for k in keys):
                row, status = f'| {quest} | {kind} | {sid} | {",".join(keys)} | {need} | not checked yet |', 'UNCHECKED'
            else:
                have = sum(entry['mins'][k] for k in keys)
                status = 'NOT FOUND' if not entry['copies'] else ('OK' if have >= need else 'SHORT')
                row = f'| {quest} | {kind} | {sid} | {",".join(keys)} | {need} | {have} (of {entry["copies"]} copies) |'
            rows.append(row + f' {status} |')
            if status != 'OK':
                attention.append(rows[-1])
    with open(OUT, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write('# Puzzle check (SPOILERS)\n\nGenerated by tools/quests/verify_puzzles.py: each puzzle step against the '
                 'fewest blocks any generated copy of its structure had (cached in puzzle_cache.json).\n\n'
                 '| quest | step | structure | blocks | needs | fewest found | |\n|---|---|---|---|---|---|---|\n')
        fh.write('\n'.join(rows) + '\n')
    print(f'{len(rows)} checks, {len(attention)} need attention: {os.path.relpath(OUT, ROOT)}')
    for r in attention:
        print('  ' + r)


if __name__ == '__main__':
    main()
