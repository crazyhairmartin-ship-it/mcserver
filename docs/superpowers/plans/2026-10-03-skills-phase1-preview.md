# FOTF Skills Phase 1 (Preview Trees) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** All 12 approved talent trees playable in game as Pufferfish's Skills trees whose nodes do nothing yet, on a separate test server and test Prism instance, so Dylan and Fionah can click through them and tune layout and wording.

**Architecture:** The tree data moves from the design page's JavaScript into `tools/skills/trees.json` (single source of truth). A Python generator turns it into Pufferfish's Skills config files under `config/puffish_skills/`. Everything happens on the `skills-preview` branch of the pack repo; a second Docker server (`server-test/`, port 25566, fresh world) and a copied Prism instance install that branch. The real server, world and Dylan's normal instance stay on `main` and are never touched.

**Tech Stack:** Pufferfish's Skills 0.19.x (Modrinth `skills`, Forge 1.20.1), packwiz, Python 3.12 + pytest, Node (one-off data export), Docker (itzg/minecraft-server:java17), Prism Launcher.

**Spec:** `docs/superpowers/specs/2026-10-03-skills-design.md` (+ trees in `docs/superpowers/specs/2026-10-03-skill-trees.html`)

## Global Constraints

- Minecraft 1.20.1, Forge 47.4.23, server image `itzg/minecraft-server:java17` (from the project setup).
- Every skill caps at level 50, 1 point per level; tier gates are points spent in that tree: tier 1 = 0, tier 2 = 5, tier 3 = 10, tier 4 = 15, tier 5 = 25.
- Node ranks cost 1 point each, except capstones, Weaponsmith and Armourer: single nodes costing 3 points.
- Choice tiers: taking one branch excludes the other branch only.
- "Needs X" nodes require every rank of X first.
- Phase 1 nodes use Pufferfish's `dummy` reward (no effects). No XP sources yet; points are granted by command.
- Never edit, restart or redeploy the real server (`server/`) or push to `main` in this phase.
- Pufferfish's Skills config: `config/puffish_skills/config.json` (`version` 3, `categories` list), one folder per category with `category.json`, `definitions.json`, `skills.json`, `connections.json`.
- Shell heredocs mangle quotes/backslashes on this machine: write files with the editor tool, not heredocs.

## Review Focus

1. A node with a prerequisite (e.g. Prospector II) must not be unlockable before every rank of its prerequisite, even though its tier is open; test `test_needs_node_not_root_and_linked`.
2. Taking one branch of a choice tier must lock the other branch and nothing else in that tier; test `test_choice_tier_exclusive_only_between_branches`.
3. Rank 2 of a node must never be unlockable before rank 1; test `test_rank_chain`.
4. Renaming a tree (Woodcutting became Foraging) must not leave a stale category folder that still loads in game; test `test_generator_removes_stale_categories`.
5. Names with apostrophes or spaces ("Miner's Might", "Berserker's Axe") must become valid, unique ids; test `test_slug_and_unique_ids`.

---

## File Structure

| Path (pack repo) | Responsibility |
|---|---|
| `tools/skills/export_trees.js` | One-off: reads `TREES`/`TIERS` from the design page, writes `tools/skills/trees.json` |
| `tools/skills/trees.json` | Source of truth for all trees (tiers, nodes, icons) |
| `tools/skills/make_skill_trees.py` | Generator: `trees.json` -> `config/puffish_skills/**` |
| `tools/skills/test_make_skill_trees.py` | pytest tests for the generator |
| `config/puffish_skills/**` | Generated Pufferfish config (committed, shipped by packwiz) |
| `mods/skills.pw.toml` | Pufferfish's Skills (packwiz, Modrinth) |
| `../server-test/docker-compose.yml` (outside the repo, next to `server/`) | Test server on port 25566, installs the `skills-preview` branch |

---

### Task 1: Branch and tree data export

**Files:**
- Create: `tools/skills/export_trees.js`
- Create: `tools/skills/trees.json` (generated)

**Interfaces:**
- Produces: `tools/skills/trees.json` with shape
  `{"tiers":[{"n":1,"req":0},...], "trees":[{"id":"mining","name":"Mining","xp":"...","icon":"minecraft:iron_pickaxe","background":"minecraft:textures/block/stone.png","nodes":[{"t":1,"name":"Stone Sense","r":5,"d":"...","c":1,"b":null,"cap":false,"needs":null,"syn":null}]}]}`

- [ ] **Step 1: Create the branch**

```bash
cd "C:/Users/Dylan/Documents/Minecraft server/pack"
git checkout -b skills-preview
```

- [ ] **Step 2: Write the exporter** (`tools/skills/export_trees.js`)

```js
// One-off: pull TIERS and TREES out of the design page and write tools/skills/trees.json.
const fs = require('fs');
const path = require('path');
const page = fs.readFileSync(path.join(__dirname, '..', '..', 'docs', 'superpowers', 'specs', '2026-10-03-skill-trees.html'), 'utf8');
const script = page.split('<script>')[1].split('const BRANCH_NAMES')[0];
const { TIERS, TREES } = new Function(script + '; return { TIERS, TREES };')();
const ICONS = {
  mining: ['minecraft:iron_pickaxe', 'minecraft:textures/block/stone.png'],
  forage: ['minecraft:iron_axe', 'minecraft:textures/block/oak_planks.png'],
  farm: ['minecraft:iron_hoe', 'minecraft:textures/block/farmland_moist.png'],
  fish: ['minecraft:fishing_rod', 'minecraft:textures/block/prismarine.png'],
  cook: ['farmersdelight:cooking_pot', 'minecraft:textures/block/bricks.png'],
  craft: ['minecraft:crafting_table', 'minecraft:textures/block/spruce_planks.png'],
  attack: ['minecraft:iron_sword', 'minecraft:textures/block/polished_andesite.png'],
  range: ['minecraft:bow', 'minecraft:textures/block/birch_planks.png'],
  defense: ['minecraft:shield', 'minecraft:textures/block/cobblestone.png'],
  agility: ['minecraft:feather', 'minecraft:textures/block/white_wool.png'],
  magic: ['minecraft:enchanted_book', 'minecraft:textures/block/purpur_block.png'],
  taming: ['minecraft:lead', 'minecraft:textures/block/hay_block_side.png'],
};
const out = {
  tiers: TIERS.map(t => ({ n: t.n, req: t.req })),
  trees: TREES.map(t => ({
    id: t.id, name: t.name, xp: t.xp, icon: ICONS[t.id][0], background: ICONS[t.id][1],
    nodes: t.nodes.map(n => ({ t: n.t, name: n.name, r: n.r, d: n.d, c: n.c || 1, b: n.b || null,
      cap: !!n.cap, needs: n.needs || null, syn: n.syn || null })),
  })),
};
fs.writeFileSync(path.join(__dirname, 'trees.json'), JSON.stringify(out, null, 2) + '\n');
console.log(`wrote ${out.trees.length} trees, ${out.trees.reduce((a, t) => a + t.nodes.length, 0)} nodes`);
```

- [ ] **Step 3: Run it**

Run: `"/c/Program Files/nodejs/node" tools/skills/export_trees.js`
Expected: `wrote 12 trees, N nodes` (N is about 190; 12 trees is required)

- [ ] **Step 4: Spot-check the JSON**

Run: `python -c "import json;d=json.load(open('tools/skills/trees.json'));print([t['id'] for t in d['trees']]);print(d['trees'][0]['nodes'][0])"`
Expected: the 12 ids `mining, forage, farm, fish, cook, craft, attack, range, defense, agility, magic, taming` and `{'t': 1, 'name': 'Stone Sense', 'r': 5, ...}`

- [ ] **Step 5: Commit**

```bash
git add tools/skills/export_trees.js tools/skills/trees.json
git commit -m "Skills preview: export approved tree data to tools/skills/trees.json"
```

---

### Task 2: Generator core (ids, definitions, rank chains, tiers)

**Files:**
- Create: `tools/skills/make_skill_trees.py`
- Test: `tools/skills/test_make_skill_trees.py`

**Interfaces:**
- Consumes: `tools/skills/trees.json` (Task 1 shape)
- Produces:
  - `slug(name: str) -> str` (lowercase, `[a-z0-9_]` only)
  - `rank_ids(node: dict) -> list[str]` (`slug_1 .. slug_r`)
  - `build_category(tree: dict, tiers: list[dict]) -> dict[str, dict]` mapping file name -> JSON content for
    `category.json`, `definitions.json`, `skills.json`, `connections.json`
  - `write_config(data: dict, out_dir: Path) -> None`

- [ ] **Step 1: Write the failing tests** (`tools/skills/test_make_skill_trees.py`)

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd tools/skills && python -m pytest -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'make_skill_trees'`

- [ ] **Step 3: Write the generator core** (`tools/skills/make_skill_trees.py`)

```python
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
        cat_dir = out_dir / tree['id']
        cat_dir.mkdir()
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd tools/skills && python -m pytest -q`
Expected: `3 passed`

- [ ] **Step 5: Commit**

```bash
git add tools/skills/make_skill_trees.py tools/skills/test_make_skill_trees.py
git commit -m "Skills preview: generator core (ids, rank chains, tier gates, dummy rewards)"
```

---

### Task 3: Prerequisites, choice tiers, capstones, layout and file output

**Files:**
- Modify: `tools/skills/test_make_skill_trees.py` (append tests)
- Modify: `tools/skills/make_skill_trees.py` (only if a test fails)
- Create: `config/puffish_skills/**` (generated)

**Interfaces:**
- Consumes: `build_category`, `write_config`, `rank_ids` from Task 2

- [ ] **Step 1: Append the tests**

```python
def test_needs_node_not_root_and_linked():
    files = g.build_category(tree('mining'), TIERS)
    assert 'root' not in files['skills.json']['prospector_ii_1']
    assert ['prospector_5', 'prospector_ii_1'] in files['connections.json']['normal']['unidirectional']


def test_choice_tier_exclusive_only_between_branches():
    files = g.build_category(tree('range'), TIERS)
    ex = files['connections.json']['exclusive']['bidirectional']
    assert ['rapid_volley_1', 'heavy_draw_1'] in ex
    assert ['fletchers_luck_1', 'seeker_1'] in ex
    named = {i for pair in ex for i in pair}
    assert 'homing_arrows_1' not in named and 'steady_hands_1' not in named


def test_capstones_cost_three_single_rank():
    defs = g.build_category(tree('craft'), TIERS)['definitions.json']
    for sid in ('masterwork_1', 'endless_workshop_1', 'weaponsmith_1', 'armourer_1'):
        assert defs[sid]['cost'] == 3, sid
    assert 'masterwork_2' not in defs
    assert defs['masterwork_1']['frame']['data']['frame'] == 'challenge'
    assert defs['weaponsmith_1']['frame']['data']['frame'] == 'goal'


def test_layout_no_overlap_and_endpoints_exist():
    for t in DATA['trees']:
        files = g.build_category(t, TIERS)
        skills = files['skills.json']
        spots = [(s['x'], s['y']) for s in skills.values()]
        assert len(spots) == len(set(spots)), t['id']
        conns = files['connections.json']
        for pair in conns['normal']['unidirectional'] + conns['exclusive']['bidirectional']:
            assert all(p in skills for p in pair), (t['id'], pair)


def test_full_tree_fits_level_cap():
    for t in DATA['trees']:
        total = 0
        for tier in TIERS:
            row = [n for n in t['nodes'] if n['t'] == tier['n']]
            total += sum(n['r'] * n['c'] for n in row if not n['b'])
            total += max([sum(n['r'] * n['c'] for n in row if n['b'] == br) for br in 'AB'] or [0])
        assert 40 <= total <= 50, (t['id'], total)


def test_generator_removes_stale_categories(tmp_path):
    out = tmp_path / 'puffish_skills'
    (out / 'wood').mkdir(parents=True)
    (out / 'wood' / 'skills.json').write_text('{}')
    g.write_config(DATA, out)
    assert not (out / 'wood').exists()
    config = json.loads((out / 'config.json').read_text())
    assert config['version'] == 3 and len(config['categories']) == 12
    assert (out / 'forage' / 'definitions.json').exists()
```

- [ ] **Step 2: Run the tests**

Run: `cd tools/skills && python -m pytest -q`
Expected: `9 passed`

- [ ] **Step 3: Generate the config**

Run: `python tools/skills/make_skill_trees.py`
Expected: `wrote 12 categories to ...\config\puffish_skills`

- [ ] **Step 4: Commit**

```bash
git add tools/skills config/puffish_skills
git commit -m "Skills preview: prerequisites, choice tiers, capstones, layout; generated Pufferfish config"
```

---

### Task 4: Add Pufferfish's Skills to the branch pack and verify installs

**Files:**
- Create: `mods/skills.pw.toml`
- Modify: `index.toml`, `pack.toml` (packwiz refresh)

- [ ] **Step 1: Add the mod from Modrinth**

Run: `printf 'y\n' | packwiz mr add skills`
Expected: `Project "Pufferfish's Skills" successfully added! (puffish_skills-0.19.x-1.20.1-forge.jar)`. `side` stays `"both"` (the skill screen is client-side).

- [ ] **Step 2: Refresh and confirm the config is indexed**

Run: `packwiz refresh && grep -c "puffish_skills" index.toml`
Expected: a count of 49 (config.json + 12 x 4 category files)

- [ ] **Step 3: Test the client install from a clean folder**

Run in one shell: `packwiz serve --port 8088`
Run in another:
```bash
MSYS_NO_PATHCONV=1 docker run --rm -v "C:/Users/Dylan/Documents/Minecraft server/server/data/packwiz-installer-v0.5.14-dist.jar:/pi.jar:ro" eclipse-temurin:17-jre sh -c "mkdir /t && cd /t && java -cp /pi.jar link.infra.packwiz.installer.Main -g -s client http://host.docker.internal:8088/pack.toml 2>&1 | grep -iE 'failed|excluded|Finished'; ls mods | grep -i puffish; ls config/puffish_skills | head -3"
```
Expected: `Finished successfully!`, the puffish jar, and `agility attack config.json`. Stop `packwiz serve` (Ctrl+C) afterwards.

- [ ] **Step 4: Commit and push the branch (not main)**

```bash
git add mods/skills.pw.toml index.toml pack.toml
git commit -m "Skills preview: add Pufferfish's Skills"
git push -u origin skills-preview
```

---

### Task 5: Test server and test Prism instance

**Files:**
- Create: `C:/Users/Dylan/Documents/Minecraft server/server-test/docker-compose.yml` (outside the pack repo)

- [ ] **Step 1: Write the test server compose file**

```yaml
# Throwaway test server for the skills preview. Fresh world in ./data; installs the skills-preview branch.
# Never shares anything with ../server (the real server).
services:
  mc-test:
    image: itzg/minecraft-server:java17
    container_name: fotf-test
    ports:
      - "25566:25565"
    environment:
      EULA: "TRUE"
      TYPE: FORGE
      VERSION: "1.20.1"
      FORGE_VERSION: "47.4.23"
      PACKWIZ_URL: https://raw.githubusercontent.com/crazyhairmartin-ship-it/mcserver/skills-preview/pack.toml
      MEMORY: 6G
      USE_AIKAR_FLAGS: "true"
      DIFFICULTY: peaceful
      MODE: creative
      OPS: Dylan
      MOTD: "FOTF skills test"
    volumes:
      - ./data:/data
    tty: true
    stdin_open: true
    restart: "no"
```

- [ ] **Step 2: Start it and wait for boot**

Run: `cd "C:/Users/Dylan/Documents/Minecraft server/server-test" && docker compose up -d`
Then watch: `docker logs -f fotf-test` until `Done (` appears (first boot downloads the pack, about 5-10 min).
Expected: `Done (...)! For help, type "help"`

- [ ] **Step 3: Check Pufferfish loaded the trees without warnings**

Run: `grep -iE "puffish|skills" server-test/data/logs/latest.log | head -40`
Expected: no lines with `warn`/`error`/`problem` from puffish. If there are, they name the file and field: fix the generator (e.g. wrong connections format), regenerate (Task 3 Step 3), commit, push, and restart the test server (`docker compose restart`).

- [ ] **Step 4: Confirm the points command**

Run: `docker exec fotf-test rcon-cli "help puffish_skills"`
Expected: subcommands including `points`. Note the exact `points add` syntax for the checklist below.

- [ ] **Step 5: Hand Dylan the Prism checklist** (he does these clicks; Prism must not be edited while it runs)

1. In Prism, right-click the **1.20.1** instance > **Copy**, name it **FOTF Test**.
2. **FOTF Test** > **Edit** > **Settings** > **Custom commands** > Pre-launch command:
   `"$INST_JAVA" -jar packwiz-installer-bootstrap.jar https://raw.githubusercontent.com/crazyhairmartin-ship-it/mcserver/skills-preview/pack.toml`
3. Launch **FOTF Test**, Multiplayer > Add Server > `localhost:25566`.
4. In game: `/puffish_skills points add Dylan mining 50` (and the other 11 tree ids: forage farm fish cook craft attack range defense agility magic taming), then open the skill screen (the mod's key, default **K**; check Controls).

- [ ] **Step 6: In-game verification (Dylan + Claude together)**

Expected for every tree:
- Tier rows unlock at 0 / 5 / 10 / 15 / 25 points spent.
- Rank 2 of a node can't be taken before rank 1.
- Prospector II (and every other "Needs ..." node) stays locked until all ranks of its prerequisite are taken.
- Taking Rapid Volley locks Heavy Draw and nothing else; capstones cost 3 points.
- Titles, descriptions and "(feeds X)" read correctly.
Record layout/wording changes Dylan asks for in `tools/skills/trees.json`, regenerate, push the branch, restart the test server.

- [ ] **Step 7: Commit any tree tweaks**

```bash
git add tools/skills/trees.json config/puffish_skills
git commit -m "Skills preview: layout and wording from first playtest"
git push
```

---

## Later phases (separate plans, written when phase 1 is approved)

- **Phase 2, add-on core:** `extras/fotfskills` (javac in Docker like fotfmail), Pufferfish API registration (`RewardFactory`, `ExperienceSourceFactory`), XP sources and `experience.json` (level cap 50, curve), common perks (save resources, extra output, speed, flat/percent stats), weapon type tags from `docs/superpowers/specs/2026-10-03-weapons.csv`.
- **Phase 3, unique perks:** homing, multishot, green thumb, scavenging, Loyal Guard, Mana Shield, second wind, guaranteed crafting results, cross-skill nodes.
- **Phase 4, systems:** total-level hearts/stamina (replaces Paragliders, removed in the same release), tree reset for XP levels, standalone pet revival (Pet Memento), single grappling hook with Agility upgrades (other hooks, upgrade items and modifier block removed).
- **Phase 5, tuning and release:** balance pass on the test server, then merge to `main` and restart the real server with players warned.
