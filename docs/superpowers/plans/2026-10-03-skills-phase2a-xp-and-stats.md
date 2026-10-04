# Skills Phase 2a: XP and Stat Nodes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the preview trees into working skills: every tree earns XP from the activity that trains it (level cap 50, one point per level), and every node whose whole effect is a plain attribute (damage, armour, health, mana...) actually applies it.

**Architecture:** The generator (`tools/skills/make_skill_trees.py`) gains two hand-written data files, `xp.json` (XP curve plus each tree's XP sources) and `perks.json` (attribute rewards per node). It writes them into each category's `experience.json` and into the rank definitions' `rewards`. XP the built-in Pufferfish sources can't express comes from the fotfskills add-on as custom XP source types:
- `fotfskills:cast_spell`
- `fotfskills:tame`
- `fotfskills:shield_block`
- `fotfskills:cook`
- `fotfskills:craft_gear`
- `fotfskills:move`

Everything stays on the `skills-preview` branch and the test server. Nothing reaches main.

**Tech Stack:** Python 3.12 + pytest (generator). Java 17 javac in Docker against SRG names (add-on, `extras/fotfskills/build.sh`). Pufferfish's Skills 0.19.1 API (`SkillsAPI.registerExperienceSource`, `SkillsAPI.updateExperienceSources`). Forge 47.4.23 events. One common mixin.

**Spec:** `docs/superpowers/specs/2026-10-03-skills-design.md` (sections "Pacing", "XP sources", "Perk types", "Phases" item 2)

## Global Constraints

- Every skill caps at **level 50**, 1 point per level. XP for next level = `30 + 12 × level^1.35` (the spec's starting curve, tuned later).
- Bonuses are opt-in power only; nothing makes the world harder.
- Progress is per player and saved on the server; XP is personal (no `team_sharing`).
- Combat XP comes from landed hits (damage dealt), not kills. Defense XP comes from hits taken from mobs and hits blocked with a shield. Falls, fire, drowning and self-inflicted damage give no Defense XP.
- Node ids keep the `<slug>_<k>` scheme. The client mixin (SkillStacks) groups ranks by that pattern plus the same x/y.
- Pufferfish stays pinned at 0.19.1. fotfskills declares `[0.19.1,0.19.2)`.
- Client-only code stays in the mixin config's `"client"` list. New server code must not touch client classes; the dedicated server must boot clean.
- Run `packwiz refresh` after pack changes. After each add-on build, the sha512 in `mods/fotfskills.pw.toml` is updated by hand.
- The test server is started with `PACK_REF=<pushed commit sha> docker compose up -d` in `server-test/` (raw.githubusercontent caches branch URLs).

## Review Focus

1. **Player-placed blocks.** Placing silk-touched ores or logs and mining them again gives Mining/Foraging XP; 2a does not block this (tracking placed blocks is phase 2b). Expected: noted, not exploitable for more than the block's own XP.
2. **Craft loops.** Edible items made in a crafting grid (e.g. apples back out of a crate) must give no Cooking XP. `CookSource` skips the crafting grid (`CraftingMenu`, `InventoryMenu`); test in game.
3. **Fractional XP.** Pufferfish rounds every event with `Math.round`, so a source worth under 0.5 per event gives nothing. Movement uses an accumulator (`MoveBank`); damage-scaled sources must give at least 1 XP for a 1-damage hit.
4. **Mod absent.** If Iron's or Ars is missing, the add-on must still load. Cast listeners are registered only when `ModList.get().isLoaded(...)`.
5. **Attribute ids.** A wrong attribute id makes Pufferfish reject the whole category ("Expected a valid player attribute"). The test-server boot log must show `Mod configuration loaded successfully!`

---

### Task 1: XP curve and sources in the generator

**Files:**
- Create: `tools/skills/xp.json`
- Modify: `tools/skills/make_skill_trees.py` (`build_category` returns `experience.json`; module docstring)
- Test: `tools/skills/test_make_skill_trees.py`

**Interfaces:**
- Consumes: `trees.json` tree ids (`mining forage farm fish cook craft attack range defense agility magic taming`)
- Produces: `build_category(tree, tiers, xp=None, perks=None)` returns `experience.json` when `xp` is given. `write_config(data, out_dir, xp=None, perks=None)`. `load(name)` reads a JSON file next to the generator. Task 2 adds `perks`.

- [ ] **Step 1: Write the failing tests**

Append to `tools/skills/test_make_skill_trees.py`:

```python
XP = json.loads((Path(__file__).parent / 'xp.json').read_text(encoding='utf-8'))


def test_every_tree_has_xp_sources_and_the_spec_curve():
    for t in DATA['trees']:
        exp = g.build_category(t, TIERS, xp=XP)['experience.json']
        assert exp['level_limit'] == 50
        assert exp['experience_per_level'] == {'type': 'expression', 'data': {'expression': '30 + 12 * level ^ 1.35'}}
        assert exp['sources'], t['id']
        for s in exp['sources']:
            assert s['type'].startswith(('puffish_skills:', 'fotfskills:')) and 'data' in s


def test_combat_xp_is_from_hits_and_defense_ignores_environment():
    types = {t['id']: [s['type'] for s in g.build_category(t, TIERS, xp=XP)['experience.json']['sources']]
             for t in DATA['trees']}
    assert types['attack'] == ['puffish_skills:deal_damage']
    assert types['range'] == ['puffish_skills:deal_damage']
    assert 'puffish_skills:kill_entity' not in sum(types.values(), [])
    assert set(types['defense']) == {'puffish_skills:take_damage', 'fotfskills:shield_block'}
    defense = g.build_category(tree('defense'), TIERS, xp=XP)['experience.json']['sources']
    taken = [s for s in defense if s['type'] == 'puffish_skills:take_damage']
    assert len(taken) == 2   # one source for melee hits, one for projectile hits: falls/fire/drowning match neither
    assert {op['type'] for s in taken for op in s['data']['variables']['counts']['operations']} >= {'get_damage_source'}


def test_no_experience_file_without_xp_data():
    assert 'experience.json' not in g.build_category(tree('mining'), TIERS)


def test_written_config_has_experience_per_category(tmp_path):
    g.write_config(DATA, tmp_path, xp=XP)
    for t in DATA['trees']:
        assert (tmp_path / 'categories' / t['id'] / 'experience.json').exists()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest -q -p no:cacheprovider tools/skills`
Expected: FAIL. The collection error is `FileNotFoundError ... xp.json`.

- [ ] **Step 3: Create `tools/skills/xp.json`**

Starting values are rough; phase 4 tunes them. `curve` is shared. `sources` is keyed by tree id and copied verbatim into `experience.json`.

```json
{
  "level_limit": 50,
  "curve": "30 + 12 * level ^ 1.35",
  "sources": {
    "mining": [
      {"type": "puffish_skills:mine_block", "data": {
        "variables": {
          "stone": {"operations": [{"type": "get_mined_block_state"}, {"type": "puffish_skills:test", "data": {"block": "#minecraft:base_stone_overworld"}}]},
          "nether": {"operations": [{"type": "get_mined_block_state"}, {"type": "puffish_skills:test", "data": {"block": "#minecraft:base_stone_nether"}}]},
          "ore": {"operations": [{"type": "get_mined_block_state"}, {"type": "puffish_skills:test", "data": {"block": "#forge:ores"}}]},
          "gem": {"operations": [{"type": "get_mined_block_state"}, {"type": "puffish_skills:test", "data": {"block": "#forge:ores/diamond"}}]},
          "emerald": {"operations": [{"type": "get_mined_block_state"}, {"type": "puffish_skills:test", "data": {"block": "#forge:ores/emerald"}}]}
        },
        "experience": [
          {"condition": "gem | emerald", "expression": "20"},
          {"condition": "ore", "expression": "6"},
          {"condition": "stone | nether", "expression": "1"}
        ]}}
    ],
    "forage": [
      {"type": "puffish_skills:mine_block", "data": {
        "variables": {"log": {"operations": [{"type": "get_mined_block_state"}, {"type": "puffish_skills:test", "data": {"block": "#minecraft:logs"}}]}},
        "experience": [{"condition": "log", "expression": "2"}]}},
      {"type": "puffish_skills:break_block", "data": {
        "variables": {
          "flower": {"operations": [{"type": "get_broken_block_state"}, {"type": "puffish_skills:test", "data": {"block": "#minecraft:flowers"}}]},
          "brown": {"operations": [{"type": "get_broken_block_state"}, {"type": "puffish_skills:test", "data": {"block": "minecraft:brown_mushroom"}}]},
          "red": {"operations": [{"type": "get_broken_block_state"}, {"type": "puffish_skills:test", "data": {"block": "minecraft:red_mushroom"}}]}
        },
        "experience": [{"condition": "flower | brown | red", "expression": "1"}]}}
    ],
    "farm": [
      {"type": "puffish_skills:break_block", "data": {
        "variables": {
          "crop": {"operations": [{"type": "get_broken_block_state"}, {"type": "puffish_skills:test", "data": {"block": "#minecraft:crops", "state": {"age": "7"}}}]},
          "beet": {"operations": [{"type": "get_broken_block_state"}, {"type": "puffish_skills:test", "data": {"block": "minecraft:beetroots", "state": {"age": "3"}}}]}
        },
        "experience": [{"condition": "crop | beet", "expression": "3"}]}},
      {"type": "puffish_skills:increase_stat", "data": {
        "variables": {"bred": {"operations": [{"type": "get_stat"}, {"type": "puffish_skills:test", "data": {"stat": "minecraft.custom:minecraft.animals_bred"}}]}},
        "experience": [{"condition": "bred", "expression": "6"}]}}
    ],
    "fish": [
      {"type": "puffish_skills:fish_item", "data": {"variables": {}, "experience": "8"}}
    ],
    "cook": [
      {"type": "fotfskills:cook", "data": {"per_nutrition": 1.0}}
    ],
    "craft": [
      {"type": "fotfskills:craft_gear", "data": {"per_item": 5}},
      {"type": "puffish_skills:smelt_item", "data": {
        "variables": {"ingot": {"operations": [{"type": "get_smelted_item_stack"}, {"type": "puffish_skills:test", "data": {"item": "#forge:ingots"}}]}},
        "experience": [{"condition": "ingot", "expression": "1"}]}}
    ],
    "attack": [
      {"type": "puffish_skills:deal_damage", "data": {
        "variables": {
          "damage": {"operations": [{"type": "get_dealt_damage"}]},
          "melee": {"operations": [{"type": "get_damage_source"}, {"type": "puffish_skills:is_melee"}]}
        },
        "experience": [{"condition": "melee", "expression": "max(damage, 1)"}],
        "anti_farming_per_entity": {"limit_per_entity": 40, "reset_after_seconds": 300}}}
    ],
    "range": [
      {"type": "puffish_skills:deal_damage", "data": {
        "variables": {
          "damage": {"operations": [{"type": "get_dealt_damage"}]},
          "projectile": {"operations": [{"type": "get_damage_source"}, {"type": "puffish_skills:is_projectile"}]}
        },
        "experience": [{"condition": "projectile", "expression": "max(damage, 1)"}],
        "anti_farming_per_entity": {"limit_per_entity": 40, "reset_after_seconds": 300}}}
    ],
    "defense": [
      {"type": "puffish_skills:take_damage", "data": {
        "variables": {
          "damage": {"operations": [{"type": "get_taken_damage"}]},
          "counts": {"operations": [{"type": "get_damage_source"}, {"type": "puffish_skills:is_melee"}]}
        },
        "experience": [{"condition": "counts", "expression": "max(damage * 1.5, 1)"}]}},
      {"type": "puffish_skills:take_damage", "data": {
        "variables": {
          "damage": {"operations": [{"type": "get_taken_damage"}]},
          "counts": {"operations": [{"type": "get_damage_source"}, {"type": "puffish_skills:is_projectile"}]}
        },
        "experience": [{"condition": "counts", "expression": "max(damage * 1.5, 1)"}]}},
      {"type": "fotfskills:shield_block", "data": {"per_damage": 1.5}}
    ],
    "agility": [
      {"type": "fotfskills:move", "data": {"meters_per_xp": 20}}
    ],
    "magic": [
      {"type": "fotfskills:cast_spell", "data": {"per_mana": 0.25}}
    ],
    "taming": [
      {"type": "fotfskills:tame", "data": {"experience": 30}},
      {"type": "puffish_skills:deal_damage", "data": {
        "tamed": "only",
        "variables": {"damage": {"operations": [{"type": "get_dealt_damage"}]}},
        "experience": "max(damage * 0.75, 1)",
        "anti_farming_per_entity": {"limit_per_entity": 40, "reset_after_seconds": 300}}},
      {"type": "puffish_skills:increase_stat", "data": {
        "variables": {"bred": {"operations": [{"type": "get_stat"}, {"type": "puffish_skills:test", "data": {"stat": "minecraft.custom:minecraft.animals_bred"}}]}},
        "experience": [{"condition": "bred", "expression": "6"}]}}
    ]
  }
}
```

- [ ] **Step 4: Implement in the generator**

In `make_skill_trees.py`, add after `ICONS = ...`:

```python
def load(name):
    return json.loads((HERE / name).read_text(encoding='utf-8'))
```

Change the signature to `def build_category(tree, tiers, xp=None, perks=None):`. Replace its `return` with:

```python
    files = {'category.json': category, 'definitions.json': definitions, 'skills.json': skills,
             'connections.json': connections}
    if xp is not None:
        files['experience.json'] = {
            'level_limit': xp['level_limit'],
            'experience_per_level': {'type': 'expression', 'data': {'expression': xp['curve']}},
            'sources': xp['sources'][tree['id']],
        }
    return files
```

Change `write_config(data, out_dir)` to `write_config(data, out_dir, xp=None, perks=None)` and call `build_category(tree, data['tiers'], xp, perks)`. In `main()`, call `write_config(data, OUT, load('xp.json'), load('perks.json') if (HERE / 'perks.json').exists() else None)`. In the module docstring, replace the "Phase 1 (preview): nodes have no rewards" paragraph with:

```
XP: tools/skills/xp.json -> categories/<id>/experience.json (curve, level cap, sources; fotfskills:* types come
from the add-on). Rewards: tools/skills/perks.json -> each rank definition's "rewards" (phase 2a: attributes).
Node ids must stay <slug>_<k>: the add-on's client mixin groups ranks by that pattern.
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `python -m pytest -q -p no:cacheprovider tools/skills`
Expected: PASS (20 passed).

- [ ] **Step 6: Commit**

```bash
python tools/skills/make_skill_trees.py
git add tools/skills config/puffish_skills
git commit -m "Skills 2a: XP curve and per-tree XP sources (experience.json)"
```

---

### Task 2: Attribute rewards for stat nodes

**Files:**
- Create: `tools/skills/perks.json`
- Modify: `tools/skills/make_skill_trees.py` (`build_category` adds `rewards`)
- Test: `tools/skills/test_make_skill_trees.py`

**Interfaces:**
- Consumes: `build_category(tree, tiers, xp, perks)` from Task 1; node slugs from `slug()`.
- Produces: `perks.json` shaped `{"<tree id>": {"<node slug>": [<reward>, ...]}}`. Each listed reward is added to **every** rank definition of that node, so N ranks give N times the value (Pufferfish applies each unlocked definition's rewards).

- [ ] **Step 1: Write the failing tests**

```python
PERKS = json.loads((Path(__file__).parent / 'perks.json').read_text(encoding='utf-8'))


def test_stat_nodes_get_one_attribute_reward_per_rank():
    defs = g.build_category(tree('attack'), TIERS, XP, PERKS)['definitions.json']
    reward = {'type': 'puffish_skills:attribute',
              'data': {'attribute': 'minecraft:generic.attack_damage', 'value': 0.3, 'operation': 'addition'}}
    for k in range(1, 6):
        assert defs[f'sharpened_{k}']['rewards'] == [reward]
    assert 'rewards' not in defs['momentum_1']          # not a plain attribute: phase 2b/3
    assert 'rewards' not in defs['tier_1_label']


def test_mana_pool_raises_both_mods():
    defs = g.build_category(tree('magic'), TIERS, XP, PERKS)['definitions.json']
    attrs = {r['data']['attribute'] for r in defs['mana_pool_1']['rewards']}
    assert attrs == {'irons_spellbooks:max_mana', 'ars_nouveau:ars_nouveau.perk.max_mana'}


def test_perks_only_name_real_nodes_and_valid_operations():
    for tree_id, nodes in PERKS.items():
        slugs = {g.slug(n['name']) for n in tree(tree_id)['nodes']}
        for node_slug, rewards in nodes.items():
            assert node_slug in slugs, (tree_id, node_slug)
            for r in rewards:
                assert r['type'] == 'puffish_skills:attribute'
                assert r['data']['operation'] in {'addition', 'multiply_base', 'multiply_total'}
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest -q -p no:cacheprovider tools/skills`
Expected: FAIL with `FileNotFoundError ... perks.json`.

- [ ] **Step 3: Create `tools/skills/perks.json`**

Only nodes whose **whole** effect is an attribute are listed. Partial matches (Riptide Runner, Bulwark, Staff Adept...) wait for the add-on perks in 2b/3. Iron's percent attributes use `multiply_base` (spell power base 1.0). Cooldown and cast-time reduction are additive fractions.

```json
{
  "attack": {
    "sharpened":    [{"type": "puffish_skills:attribute", "data": {"attribute": "minecraft:generic.attack_damage", "value": 0.3, "operation": "addition"}}],
    "sharpened_ii": [{"type": "puffish_skills:attribute", "data": {"attribute": "minecraft:generic.attack_damage", "value": 0.3, "operation": "addition"}}]
  },
  "defense": {
    "toughened":   [{"type": "puffish_skills:attribute", "data": {"attribute": "minecraft:generic.armor", "value": 0.5, "operation": "addition"}}],
    "vitality":    [{"type": "puffish_skills:attribute", "data": {"attribute": "minecraft:generic.max_health", "value": 1, "operation": "addition"}}],
    "vitality_ii": [{"type": "puffish_skills:attribute", "data": {"attribute": "minecraft:generic.max_health", "value": 1, "operation": "addition"}}],
    "iron_skin":   [{"type": "puffish_skills:attribute", "data": {"attribute": "minecraft:generic.armor_toughness", "value": 0.5, "operation": "addition"}}]
  },
  "magic": {
    "mana_pool": [
      {"type": "puffish_skills:attribute", "data": {"attribute": "irons_spellbooks:max_mana", "value": 10, "operation": "addition"}},
      {"type": "puffish_skills:attribute", "data": {"attribute": "ars_nouveau:ars_nouveau.perk.max_mana", "value": 10, "operation": "addition"}}
    ],
    "mana_pool_ii": [
      {"type": "puffish_skills:attribute", "data": {"attribute": "irons_spellbooks:max_mana", "value": 10, "operation": "addition"}},
      {"type": "puffish_skills:attribute", "data": {"attribute": "ars_nouveau:ars_nouveau.perk.max_mana", "value": 10, "operation": "addition"}}
    ],
    "focus":         [{"type": "puffish_skills:attribute", "data": {"attribute": "irons_spellbooks:spell_power", "value": 0.03, "operation": "multiply_base"}}],
    "flow":          [{"type": "puffish_skills:attribute", "data": {"attribute": "irons_spellbooks:mana_regen", "value": 0.05, "operation": "multiply_base"}}],
    "cooldown_flow": [{"type": "puffish_skills:attribute", "data": {"attribute": "irons_spellbooks:cooldown_reduction", "value": 0.05, "operation": "addition"}}]
  },
  "agility": {
    "quick_casting": [{"type": "puffish_skills:attribute", "data": {"attribute": "irons_spellbooks:cast_time_reduction", "value": 0.05, "operation": "addition"}}]
  }
}
```

- [ ] **Step 4: Implement**

In `build_category`, after the `extra_description` lines inside the rank loop, add:

```python
                rewards = (perks or {}).get(tree['id'], {}).get(slug(n['name']))
                if rewards:
                    definitions[sid]['rewards'] = rewards
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `python -m pytest -q -p no:cacheprovider tools/skills`
Expected: PASS (23 passed).

- [ ] **Step 6: Commit**

```bash
python tools/skills/make_skill_trees.py
git add tools/skills config/puffish_skills
git commit -m "Skills 2a: attribute rewards for stat nodes (perks.json)"
```

---

### Task 3: Add-on XP sources

**Files:**
- Create: `extras/fotfskills/src/fotfskills/xp/AmountSource.java`, `XpSources.java`, `MoveBank.java`, `ForgeXpEvents.java`, `IronsCastXp.java`, `ArsCastXp.java`
- Create: `extras/fotfskills/src/fotfskills/mixin/ItemStackCraftedMixin.java`
- Create: `extras/fotfskills/test/fotfskills/xp/MoveBankTest.java`, `extras/fotfskills/test.sh`
- Modify: `extras/fotfskills/src/fotfskills/FotfSkills.java`, `extras/fotfskills/res/fotfskills.mixins.json`, `extras/fotfskills/res/META-INF/mods.toml` (description)

**Interfaces:**
- Consumes: source ids and data keys from `xp.json` (Task 1):

  | Source | Data key |
  |---|---|
  | `fotfskills:cast_spell` | `per_mana` |
  | `fotfskills:tame` | `experience` |
  | `fotfskills:shield_block` | `per_damage` |
  | `fotfskills:cook` | `per_nutrition` |
  | `fotfskills:craft_gear` | `per_item` |
  | `fotfskills:move` | `meters_per_xp` |

- Produces: `AmountSource.award(ServerPlayer, String kind, double amount)`, which gives every configured source of that kind `round(amount × factor)` XP, at least 1 when amount > 0. `MoveBank.add(double meters, double metersPerXp)` returns the whole XP earned and keeps the remainder.

- [ ] **Step 1: Write the failing test for the pure logic**

`extras/fotfskills/test/fotfskills/xp/MoveBankTest.java`:

```java
package fotfskills.xp;

/** Plain-java test (no JUnit in the build container): exits non-zero on failure. Run: sh test.sh */
public final class MoveBankTest {
    public static void main(String[] args) {
        MoveBank bank = new MoveBank();
        check(bank.add(0.28, 20) == 0, "a sprint tick is not a whole XP");
        for (int i = 0; i < 70; i++) bank.add(0.28, 20);       // 71 ticks x 0.28 m = 19.88 m
        check(bank.add(0.28, 20) == 1, "the 72nd tick crosses 20 m");
        check(bank.add(45, 20) == 2, "45 m more gives 2 and keeps 5.16 m");
        check(Math.abs(bank.remainder() - 5.16) < 1e-6, "remainder kept");
        check(AmountSource.scaled(0.3, 1.0) == 1, "a positive amount gives at least 1 XP");
        check(AmountSource.scaled(0, 1.0) == 0, "zero gives none");
        check(AmountSource.scaled(7, 1.5) == 11, "7 x 1.5 = 10.5 rounds to 11");
        System.out.println("MoveBankTest ok");
    }

    private static void check(boolean ok, String what) {
        if (!ok) { System.out.println("FAIL: " + what); System.exit(1); }
    }
}
```

`extras/fotfskills/test.sh`, which compiles `src` + `test` like build.sh and runs the test:

```bash
#!/bin/bash
# Runs the add-on's plain-java tests (pure logic only; game hooks are checked in game). Same classpath as build.sh.
set -euo pipefail
cd "$(dirname "$0")"
PRISM_LIBS=${PRISM_LIBS:-C:/Users/Dylan/AppData/Roaming/PrismLauncher/libraries}
SERVER_DATA=${SERVER_DATA:-C:/Users/Dylan/Documents/Minecraft server/server-test/data}
MSYS_NO_PATHCONV=1 docker run --rm \
  -v "$(pwd -W 2>/dev/null || pwd):/w" -v "$PRISM_LIBS:/libs:ro" -v "$SERVER_DATA:/data:ro" -w /w \
  eclipse-temurin:17-jdk sh -c '
    set -e
    CP=$(find /libs -name "*.jar" ! -name "minecraft-*-client.jar" ! -name "*-extra.jar" ! -name "*-slim.jar" \
           ! -path "*/forge/1.20.1-47.4.10/*" | tr "\n" ":")
    CP="$CP$(ls /data/libraries/net/minecraftforge/forge/1.20.1-47.4.23/forge-1.20.1-47.4.23-universal.jar):$(ls /data/mods/*.jar | tr "\n" ":")"
    rm -rf /tmp/t && mkdir -p /tmp/t
    javac --release 17 -proc:none -nowarn -cp "$CP" -d /tmp/t $(find src/fotfskills/xp test -name "*.java")
    java -cp "/tmp/t:$CP" fotfskills.xp.MoveBankTest
  '
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `bash extras/fotfskills/test.sh`
Expected: FAIL. javac reports `cannot find symbol: class MoveBank` (and `AmountSource`).

- [ ] **Step 3: Implement the sources**

`src/fotfskills/xp/MoveBank.java`:

```java
package fotfskills.xp;

/** Banks distance between ticks: Pufferfish rounds each XP event, so tiny per-tick amounts must be pooled. */
public final class MoveBank {
    private double meters;

    /** Adds distance; returns whole XP earned (one per metersPerXp) and keeps the remainder. */
    public int add(double moved, double metersPerXp) {
        meters += moved;
        int xp = (int) Math.floor(meters / metersPerXp);
        meters -= xp * metersPerXp;
        return xp;
    }

    public double remainder() {
        return meters;
    }
}
```

`src/fotfskills/xp/AmountSource.java`:

```java
package fotfskills.xp;

import net.minecraft.server.level.ServerPlayer;
import net.puffish.skillsmod.api.SkillsAPI;
import net.puffish.skillsmod.api.experience.source.ExperienceSource;
import net.puffish.skillsmod.api.experience.source.ExperienceSourceDisposeContext;

/**
 * One configured fotfskills XP source: a kind ("cook", "tame", ...) and the factor from its data
 * (e.g. {"per_nutrition": 1.0}). Events call award(); every category with a source of that kind gets XP.
 */
public record AmountSource(String kind, double factor) implements ExperienceSource {
    public static void award(ServerPlayer player, String kind, double amount) {
        SkillsAPI.updateExperienceSources(player, AmountSource.class,
                source -> source.kind.equals(kind) ? scaled(amount, source.factor) : 0);
    }

    /** round(amount x factor), but at least 1 for any positive amount. */
    public static int scaled(double amount, double factor) {
        if (amount <= 0) {
            return 0;
        }
        return Math.max(1, (int) Math.round(amount * factor));
    }

    @Override
    public void dispose(ExperienceSourceDisposeContext context) {
    }
}
```

`src/fotfskills/xp/XpSources.java`, which registers the six types and reads each one's single number:

```java
package fotfskills.xp;

import net.minecraft.resources.ResourceLocation;
import net.puffish.skillsmod.api.SkillsAPI;
import net.puffish.skillsmod.api.util.Problem;
import net.puffish.skillsmod.api.util.Result;

/** Registers fotfskills:<kind> XP sources; each reads one number from its data (see tools/skills/xp.json). */
public final class XpSources {
    private XpSources() {
    }

    public static void register() {
        source("cast_spell", "per_mana");
        source("tame", "experience");
        source("shield_block", "per_damage");
        source("cook", "per_nutrition");
        source("craft_gear", "per_item");
        source("move", "meters_per_xp");
    }

    private static void source(String kind, String key) {
        SkillsAPI.registerExperienceSource(new ResourceLocation("fotfskills", kind), context -> context.getData()
                .andThen(data -> data.getAsObject())
                .andThen(object -> object.getDouble(key))
                .andThen(value -> value > 0 ? Result.<AmountSource, Problem>success(new AmountSource(kind, value))
                        : Result.<AmountSource, Problem>failure(Problem.message(key + " must be above 0"))));
    }
}
```

`src/fotfskills/xp/ForgeXpEvents.java` (Forge bus) handles taming, shield blocks and movement:

```java
package fotfskills.xp;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.living.AnimalTameEvent;
import net.minecraftforge.event.entity.living.ShieldBlockEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.puffish.skillsmod.api.SkillsAPI;

/** Taming, shield blocks (Defense) and sprinting/climbing distance (Agility). */
public final class ForgeXpEvents {
    private final Map<UUID, double[]> lastPos = new HashMap<>();
    private final Map<UUID, MoveBank> banks = new HashMap<>();

    @SubscribeEvent
    public void onTame(AnimalTameEvent event) {
        if (event.getTamer() instanceof ServerPlayer player) {
            AmountSource.award(player, "tame", 1);
        }
    }

    @SubscribeEvent
    public void onShieldBlock(ShieldBlockEvent event) {
        if (event.getEntity() instanceof ServerPlayer player && event.getDamageSource().m_7639_() != null
                && event.getDamageSource().m_7639_() != player) {
            AmountSource.award(player, "shield_block", event.getBlockedDamage());
        }
    }

    @SubscribeEvent
    public void onTick(TickEvent.PlayerTickEvent event) {
        if (event.phase != TickEvent.Phase.END || !(event.player instanceof ServerPlayer player)) {
            return;
        }
        double x = player.m_20185_();
        double z = player.m_20189_();
        double[] last = lastPos.put(player.m_20148_(), new double[] {x, player.m_20186_(), z});
        if (last == null || player.m_20159_() || !(player.m_20142_() || player.m_6147_())) {
            return;
        }
        double moved = player.m_6147_() ? Math.abs(player.m_20186_() - last[1]) : Math.hypot(x - last[0], z - last[2]);
        if (moved > 2) {
            return;                 // teleport, not movement
        }
        MoveBank bank = banks.computeIfAbsent(player.m_20148_(), id -> new MoveBank());
        SkillsAPI.updateExperienceSources(player, AmountSource.class,
                source -> source.kind().equals("move") ? bank.add(moved, source.factor()) : 0);
    }

    @SubscribeEvent
    public void onLogout(PlayerEvent.PlayerLoggedOutEvent event) {
        UUID id = event.getEntity().m_20148_();
        lastPos.remove(id);
        banks.remove(id);
    }
}
```

The SRG names used above are:

| SRG name | Method |
|---|---|
| m_7639_ | DamageSource.getEntity |
| m_20148_ | getUUID |
| m_20186_ | getY |
| m_20159_ | isPassenger (riding doesn't count) |
| m_20142_ | isSprinting |
| m_6147_ | onClimbable |

If javac reports any as missing, check it with `javap` against the SRG client jar and correct it in place (a Ruling only if behaviour changes).

`src/fotfskills/xp/IronsCastXp.java` and `ArsCastXp.java` are each loaded only when that mod is present:

```java
package fotfskills.xp;

import io.redspace.ironsspellbooks.api.events.SpellOnCastEvent;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.eventbus.api.SubscribeEvent;

/** Iron's Spells cast: Magic XP by mana spent. Registered only if irons_spellbooks is loaded. */
public final class IronsCastXp {
    @SubscribeEvent
    public void onCast(SpellOnCastEvent event) {
        if (event.getEntity() instanceof ServerPlayer player) {
            AmountSource.award(player, "cast_spell", event.getManaCost());
        }
    }
}
```

```java
package fotfskills.xp;

import com.hollingsworth.arsnouveau.api.event.SpellCastEvent;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.eventbus.api.SubscribeEvent;

/** Ars Nouveau cast: Magic XP by the spell's mana cost. Registered only if ars_nouveau is loaded. */
public final class ArsCastXp {
    @SubscribeEvent
    public void onCast(SpellCastEvent event) {
        if (event.getEntity() instanceof ServerPlayer player && !event.isCanceled()) {
            AmountSource.award(player, "cast_spell", event.spell.getCost());
        }
    }
}
```

`src/fotfskills/mixin/ItemStackCraftedMixin.java` covers Cooking and Crafting. Every result slot (crafting grid, furnace/smoker, smithing table, Farmer's Delight cooking pot, other mods' stations) calls `ItemStack.onCraftedBy`:

```java
package fotfskills.mixin;

import fotfskills.xp.AmountSource;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.food.FoodProperties;
import net.minecraft.world.inventory.CraftingMenu;
import net.minecraft.world.inventory.InventoryMenu;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * Cooking XP for food taken from any station except the crafting grid (so crate/block un-crafting loops give
 * nothing), and Crafting XP for gear (damageable items) from any station. ItemStack.onCraftedBy = m_41678_.
 */
@Mixin(value = ItemStack.class, remap = false)
public abstract class ItemStackCraftedMixin {
    @Inject(method = "m_41678_", at = @At("HEAD"), remap = false)
    private void fotfskills$craftedXp(Level level, Player player, int amount, CallbackInfo ci) {
        if (!(player instanceof ServerPlayer server) || amount <= 0) {
            return;
        }
        ItemStack stack = (ItemStack) (Object) this;
        boolean grid = player.f_36096_ instanceof CraftingMenu || player.f_36096_ instanceof InventoryMenu;
        if (stack.m_41614_() && !grid) {
            FoodProperties food = stack.getFoodProperties(player);
            if (food != null) {
                AmountSource.award(server, "cook", (double) food.m_38744_() * amount);
            }
        } else if (stack.m_41763_()) {
            AmountSource.award(server, "craft_gear", amount);
        }
    }
}
```

SRG names: `f_36096_` is Player.containerMenu, `m_41614_` isEdible, `m_41763_` isDamageableItem, `m_38744_` getNutrition. `getFoodProperties(LivingEntity)` is Forge's IForgeItemStack.

`res/fotfskills.mixins.json` gets a common list:

```json
  "mixins": ["ItemStackCraftedMixin"],
```

This goes beside the existing `"client": ["SkillsScreenMixin"]`, with the same package `fotfskills.mixin`.

`src/fotfskills/FotfSkills.java`:

```java
package fotfskills;

import fotfskills.xp.ArsCastXp;
import fotfskills.xp.ForgeXpEvents;
import fotfskills.xp.IronsCastXp;
import fotfskills.xp.XpSources;
import net.minecraftforge.common.MinecraftForge;
import net.minecraftforge.fml.ModList;
import net.minecraftforge.fml.common.Mod;

/** FOTF Skills: client skill-window tweaks (mixins) plus the custom XP sources for the skill trees. */
@Mod("fotfskills")
public final class FotfSkills {
    public FotfSkills() {
        XpSources.register();
        MinecraftForge.EVENT_BUS.register(new ForgeXpEvents());
        if (ModList.get().isLoaded("irons_spellbooks")) {
            MinecraftForge.EVENT_BUS.register(new IronsCastXp());
        }
        if (ModList.get().isLoaded("ars_nouveau")) {
            MinecraftForge.EVENT_BUS.register(new ArsCastXp());
        }
    }
}
```

In `res/META-INF/mods.toml`, change the description's last sentence to: "Also adds the custom XP sources (spells, taming, shield blocks, cooking, crafting, movement); perks come later."

- [ ] **Step 4: Run the test to verify it passes, then build**

Run: `bash extras/fotfskills/test.sh`
Expected: `MoveBankTest ok`

Run: `bash extras/fotfskills/build.sh`
Expected: `Built fotfskills-1.0.0.jar`, with no javac errors. A missing SRG name gets fixed via `javap` as noted in Step 3.

- [ ] **Step 5: Commit**

```bash
H=$(sha512sum extras/fotfskills/fotfskills-1.0.0.jar | cut -d' ' -f1)
sed -i "s/^hash = .*/hash = \"$H\"/" mods/fotfskills.pw.toml
packwiz refresh
git add extras/fotfskills mods/fotfskills.pw.toml index.toml pack.toml
git commit -m "Skills 2a: add-on XP sources (spells, taming, shield blocks, cooking, crafting, movement)"
```

---

### Task 4: Test server boot and in-game XP check

**Files:**
- Modify: none, unless the boot log shows config problems (fix those in `xp.json`/`perks.json` with a test first if the generator is at fault)

**Interfaces:**
- Consumes: everything above, pushed to `skills-preview`.

- [ ] **Step 1: Push and boot**

```bash
git push origin skills-preview
cd ../server-test && docker compose down && PACK_REF=$(git -C ../pack rev-parse HEAD) docker compose up -d
```

Wait for `Done (` in `docker logs fotf-test`.

- [ ] **Step 2: Check the boot log**

Run: `docker logs fotf-test 2>&1 | grep -E "puffish_skills|fotfskills|Mixin.*(fail|error)|Expected"`
Expected: `[puffish_skills] Mod configuration loaded successfully!` and no `Expected ...` problems or mixin errors.

If Pufferfish rejects a source field (the docs describe a newer version than 0.19.1), read the exact problem path from the log. Then fix that field in `xp.json`, regenerate, push, and reboot. Each such fix is a ledger Ruling with the log line.

- [ ] **Step 3: In-game check with Dylan (FOTF Test instance, `localhost:25566`)**

Reset first: `puffish_skills points set @a <cat> 0` for each category. Then:

| Do | Expect |
|---|---|
| Mine stone, then an iron ore | Mining XP bar moves (+1, then +6) |
| Chop a log; break a flower | Foraging XP |
| Break a fully grown wheat; break unripe wheat | Farming XP only for the grown one |
| Breed two cows | Farming and Taming XP |
| Catch a fish | Fishing XP |
| Cook food in a smoker and FD cooking pot; craft apples out of a crate | Cooking XP for the first two only |
| Craft an iron pickaxe; smelt iron ore | Crafting XP for both |
| Hit a zombie (sword); shoot it (bow) | Attack XP, then Range XP |
| Let a zombie hit you; block with a shield; fall 5 blocks | Defense XP for the first two, none for the fall |
| Sprint about 40 m | Agility XP (2) |
| Cast an Iron's spell; cast an Ars spell | Magic XP |
| Tame a wolf; let it bite a mob | Taming XP |
| `/puffish_skills points set @a attack 10`, take Sharpened ×5 | Attack damage +1.5 (F3 or a weapon tooltip) |
| Take Mana Pool ×2 | Iron's and Ars max mana each +20 |

Any row that fails is debugged (superpowers:systematic-debugging) and fixed before the task completes. A row that can't work in 2a is moved to the 2b list as a Ruling.

- [ ] **Step 4: Record**

Ledger `Task 4: complete` with the boot log line and the table result. No commit unless fixes were needed (each fix is its own commit, message `Skills 2a: fix <what>`).
