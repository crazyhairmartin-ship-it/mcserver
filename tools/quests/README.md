# Quests

> **Spoilers:** everything under `src/` (and the generated `config/ftbquests/`) is the quest content itself. The
> pack owner plays the quests unspoiled; when summarising quest work for them, describe approach, difficulty,
> style and plot outline only (see the spoiler policy in `docs/superpowers/specs/2026-10-13-boss-progression.md`).

The pack's quest book is [FTB Quests](https://www.curseforge.com/minecraft/mc-mods/ftb-quests) (with FTB Teams, which
it needs, and FTB XMod Compat for KubeJS). The quests aren't made in the in-game editor: they're written as short
JSON files here and turned into FTB Quests' files by a script, the same way the field guide, cookbook and skill
trees are built.

```
tools/quests/
  src/pack.json             book title, icon, chapter groups (in order)
  src/chapters/*.json       one file per chapter; the file name is the chapter's id
  src/reward_tables/*.json  random reward tables
  src/places.json           named places in the server world (the spawn village, nearby villages) for travel tasks
  src/structure_groups.json families of structures (taverns, lighthouses, mines...) that count as one place
  structures.json           every structure in the pack, whether it generates, where and how often (make_structures.py;
                            readable list in docs/world-structures.md)
  registry.json             every item, mob, biome, structure, advancement and dimension id in the pack
  make_quests.py            checks the sources, then writes the book
  make_registry.py          rebuilds registry.json from the pack's jars
  make_structures.py        rebuilds structures.json and docs/world-structures.md from the pack's jars and config
  make_mods.py              rebuilds mods.json (every mod, its ids and what it adds)
  coverage.py               checks the quest list (src/plans/quests/) and writes docs/quest-coverage.md:
                            which mods, landmarks and artifacts have quests (spoiler-free)
  src/mod_roles.json        which mods should appear in quests (libraries, client and admin mods don't)
  src/landmarks.json        plain names, landmarks seen in the world, feature landmarks, scenery, YUNG's replacements
```

`python tools/quests/make_quests.py` checks everything and writes:
- `config/ftbquests/quests/` (the book; the script owns this folder, so in-game edits there are overwritten)
- `kubejs/startup_scripts/quest_items.generated.js` (quest items like letters)
- `kubejs/server_scripts/quest_givers.generated.js` (who gives which quest)
- `kubejs/data/fotf/tags/worldgen/structure/groups/` (the structure groups, as tags)

`--check` only checks. Nothing is written if anything's wrong: unknown or trimmed item ids (with "did you mean"
suggestions), mobs, biomes, structures, broken `after` links, duplicate ids, unknown skills or reward tables.
After changing mods, rebuild the registry: `python tools/quests/make_registry.py <mods folder> <vanilla client
extra jar> .` (the docstring says where the vanilla jar is), then the structures list the same way with
`make_structures.py` (it also reads the pack's config and `kubejs/data` overrides, so rerun it after changing those).

**Ids are permanent.** FTB Quests' internal ids are made from the chapter file name, quest `id` and task position,
so regenerating keeps everyone's progress. Renaming a chapter or quest, or reordering a quest's tasks, resets that
progress, so only do it before release. Adding quests or tasks at the end is always safe.

Run `/ftbquests reload` on the server (op) after deploying new quests; players get them straight away.

## A chapter

```json
{
  "title": "Getting Started",
  "subtitle": "Your first day in the forest",
  "icon": "minecraft:oak_sapling",
  "group": "start",
  "order": 0,
  "quests": [
    {
      "id": "first_wood",
      "title": "Timber!",
      "icon": "minecraft:oak_log",
      "after": ["welcome"],
      "text": ["Every journey starts with a tree.", "A second paragraph."],
      "tasks": [{"item": "minecraft:oak_log", "count": 4}],
      "rewards": [{"skill": "forage", "xp": 30}, {"item": "minecraft:apple", "count": 3}]
    }
  ]
}
```

Chapter fields: `title`, `subtitle`, `icon`, `group` (from pack.json), `order`, `quests`, and `links`:
`[{"to": "other_chapter:quest", "pos": [x, y]}]` shows a quest from another chapter in this one. Clicking it jumps
there; this is how the main story shows its branches.

Quest fields:

| Field | What it does |
|---|---|
| `id` | Required, `a-z 0-9 _`, unique in the chapter. Never change it after release |
| `title`, `subtitle` | Shown in the book. `&` colour codes work (`&a` green, `&l` bold) |
| `text` | Description: a string, or a list of paragraphs |
| `icon` | Item id (defaults to the first task's item) |
| `after` | Quests that must be done first: `"welcome"` in this chapter, `"getting_started:home"` in another |
| `after_any` | `true`: any one of `after` is enough instead of all |
| `pos` | `[x, y]` in the chapter. Without it quests are laid out in columns by how many steps they are from the start |
| `shape`, `size` | `circle` `square` `rsquare` `diamond` `pentagon` `hexagon` `octagon` `heart` `gear`; size 1 is normal |
| `hidden` | `"until_deps"`: invisible until the quests before it are visible |
| `optional` | Doesn't block chapter completion |
| `signature` | The artifact this quest is built around, e.g. `"artifacts:snorkel"`. Each artifact may be the signature of one quest only (a standalone quest, or one step of a main, realm or skill chain); giving an artifact from a quest that isn't built around it is a warning. `--artifacts` lists artifacts without one |
| `giver` | The quest is handed out by a villager, mob or item instead of being in the book from the start (below) |
| `discover` | The quest is found out in the world: a task (usually `structure`, `biome`, `item`, `dimension` or `stat`) that's hidden; when it's done the quest appears. E.g. `"discover": {"biome": "minecraft:cherry_grove"}` |

## Tasks

| Task | Done when |
|---|---|
| `{"item": "minecraft:wheat", "count": 64}` | The player has the items. `"consume": true` takes them; `"crafted": true` only counts crafted ones |
| `{"kill": "minecraft:zombie", "count": 5}` | Kills |
| `{"biome": "minecraft:cherry_grove"}` | Standing in the biome |
| `{"structure": "minecraft:village_plains"}` | Inside the structure. `{"structure": "#taverns"}` (no namespace) is a group from `src/structure_groups.json`, so any of its structures counts; another structure tag works as `#namespace:tag` |
| `{"dimension": "minecraft:the_nether"}` | In the dimension |
| `{"place": "reece"}` | Within the place's radius (default 48 blocks). Places are named once in `src/places.json`: `"reece": {"name": "Reece", "pos": [x, y, z], "radius": 64}` |
| `{"advancement": "minecraft:adventure/sleep_in_bed"}` | The advancement is earned |
| `{"observe": "minecraft:beehive", "ticks": 40}` | Looking at a block or mob (for this long) |
| `{"levels": 10}` | Has XP levels |
| `{"stat": "minecraft:fish_caught", "count": 50}` | A vanilla statistic reaches the count (`minecraft:walk_one_cm`, `minecraft:aviate_one_cm`, `minecraft:fish_caught`, ...) |
| `{"checkmark": "I've read this"}` | The player ticks it |
| `{"talk": "villager", "profession": "minecraft:cleric", "lines": [...]}` | Sneak + right-click that villager while on the quest; they say the lines. `"talk": "entity"` with `"entity"` (and optional `"named"`) for a mob, `"talk": "org"` with `"org"` for any representative of an organisation, `"talk": "character"` with `"character"` for a named character (plain right-click) |
| `{"encounter": {"character": "id" or "entity": "minecraft:wolf", "name": "Old Grey", "then": "talk" or "kill", "lines": [...], "arrive": "...", "health": 60, "glow": true, "distance": [8, 16], "minutes": 20, "where": {"biomes": [...], "dimension": "...", "below_y": 0, "above_y": 60}}}` | When the quest reaches this step (earlier tasks done) and `where` fits, the character or mob appears 8-16 blocks from the player. `talk`: right-click it (it can't be hurt); `kill`: defeat it. It leaves after `minutes` if ignored and comes back 2 minutes later; it's removed when the step is done. Only its player can complete it |
| `{"timed": {"seconds": 300, "goal": {"kill": "minecraft:zombie", "count": 10} or {"stat": "minecraft:fish_caught", "count": 5} or {"place": "reece"}, "lines": [...], "start": "Start"}}` | When the quest reaches this step, the player gets a clickable [Start] in chat (repeated every 5 minutes until started). Timer and progress show on the action bar; reach the goal in time to complete the step, or click [Try again] |
| `{"stage": "my_stage"}` | The player has that stage (a player tag; for scripted quests) |
| `{"drop": {"from": ["minecraft:wolf"], "chance": 0.2, "item": {"name": "Alpha's Fang"}}, "count": 1}` | A unique quest drop: while the quest is open, those mobs can drop the quest item (new `kubejs:quest_*` item, or an existing id); the task is to bring it (`"consume": false` to keep it). Drops never happen outside the quest. `"from": ["fishing"]` makes it a fished item instead (a prize fish) |

Any task can have a `"title"`. Add `"unchecked": true` for ids that only exist at runtime (Every Compat's blocks, tags).

### What counts, and when

A quest's tasks only make progress once the quest is open (everything in `after` done). Some task types look back
and some don't, which matters for bosses players can fight without the quest:

- **Only counts while the quest is open:** `kill`, `talk`, `stage`, `checkmark`.
- **Completes straight away if it's already true:** `item` (carrying it), `advancement` (earned before), `stat`
  (it reads the lifetime total), `biome`/`structure`/`dimension` (standing in it).

So a boss quest should ask for the **kill** (plus steps like crafting the eye or talking to someone), not for the
boss's drop or its advancement, so beating the boss early doesn't tick the quest.

## Rewards

| Reward | Gives |
|---|---|
| `{"item": "minecraft:emerald", "count": 5}` | Items (cosmetics are just items too) |
| `{"item": "minecraft:fishing_rod", "name": "Riverrunner", "lore": ["..."], "enchant": {"minecraft:lure": 2}, "unbreakable": true}` | A unique item: gold name, grey lore, enchantments (checked against the pack). On `minecraft:enchanted_book` the enchantments are stored like a normal enchanted book. Works in reward tables too |
| `{"skill": "farm", "xp": 150}` | Pufferfish skill XP in that tree: `mining forage farm fish cook craft attack range defense agility magic taming` |
| `{"xp": 100}` / `{"levels": 3}` | Vanilla XP points / levels |
| `{"table": "village_favours"}` | One random roll from `src/reward_tables/village_favours.json` |
| `{"command": "/say hi {p}", "title": "A surprise"}` | Runs a command as the server (`{p}` is the player) |
| `{"stage": "my_stage"}` | Adds a stage |

Any reward can have a `"title"`; `"auto": true` claims it by itself.

A reward table:

```json
{"title": "Village Favours", "icon": "minecraft:emerald", "rolls": 1,
 "rewards": [{"item": "minecraft:emerald", "count": 6, "weight": 5}, {"item": "minecraft:golden_carrot", "weight": 3}]}
```

## Quest givers

A quest with a `giver` is invisible until the player accepts it. The giver says its `lines` in chat with a
clickable `[accept]` button; accepting adds the quest to the book.

```json
"giver": {
  "type": "villager",
  "profession": "minecraft:farmer",
  "requires": ["getting_started:village"],
  "lines": ["Oh, a traveller! The crows got half my wheat this year.", "Could you bring me a stack of wheat?"],
  "accept": "I'll help"
}
```

| `type` | How the player gets the quest |
|---|---|
| `org` | Sneak + right-click any representative of the organisation (`"org": "anglers"`, from pack.json) in any village. Add `"pool": "anglers_side"` to make it part of a pool (below) |
| `character` | Right-click the named character (`"character": "id"`, from pack.json), placed in Reece with `/questnpc` |
| `villager` | Sneak + right-click a villager with that `profession` (`"any"` for all) |
| `entity` | Sneak + right-click a mob of type `entity`, optionally only one `named` something (name-tagged NPCs) |
| `drop` | The mobs in `from` drop a quest item (`chance`, default 0.05) for players who don't have the quest; right-click the item to read it |
| `item` | Right-click an item (found in a chest, given by a command...) |

`requires` lists quests that must be finished before the giver offers anything. `name` overrides the speaker's
name in chat. For `drop` and `item`, `"item"` is either an existing item id or a new quest item:
`{"name": "Water-Stained Letter", "tooltip": "Right-click to read", "texture": "minecraft:item/paper"}` (its id is
`kubejs:quest_<quest id>`, or set `"id"`). The item is used up on accepting unless `"consume": false`.

`talk` steps only answer while their quest is open (checked with FTB Quests): earlier quests done, the quest not
finished, and for a quest with a `giver` or `discover`, its first task done.

How it works: accepting adds the player tag `fq.<chapter>.<quest>`, and the quest's hidden first task waits for it
(FTB Quests reads player tags as stages). `talk` tasks add `fq.<chapter>.<quest>.talk<n>`. A quest that a giver
`requires` gets an invisible reward adding `fq.<chapter>.<quest>.done`. To reset someone's quest giver state:
`/tag <player> remove fq.<chapter>.<quest>` (and change their progress with `/ftbquests change_progress`). The
behaviour lives in `kubejs/server_scripts/quest_givers.js`.

### Organisations, pools and characters (pack.json)

```json
"organisations": [{"id": "anglers", "name": "Anglers' Society", "professions": ["minecraft:fisherman"]}],
"characters": {"elder": {"name": "...", "entity": "minecraft:villager", "profession": "minecraft:cleric",
                         "idle": ["Lines they say when they have nothing for you."]}}
```

- **Organisations:** representatives are villagers with one of the `professions`, or mobs of a listed type (e.g.
  `guardvillagers:guard`). The speaker shows as "Name (Organisation)". Without a `pool`, an organisation quest is
  storyline: any representative anywhere offers the player's next one.
- **Pools:** quests sharing a `pool` are side quests. When a representative has no storyline quest for the
  player, it offers one pool quest the player can take now, chosen by that villager's own identity, so different
  villagers (and villages) offer different ones.
- **Characters:** `/questnpc place <id>` (op) puts the character where you stand, facing your way (placing again
  moves them): it never
  despawns, doesn't move and can't be hurt. `/questnpc remove <id>` removes it (in loaded chunks), `/questnpc list`
  lists them. A plain right-click talks to a character; it never opens a trading screen, and says an `idle` line
  when it has nothing for you. Encounters can bring a character to the player instead.

All of this lives in `kubejs/server_scripts/quest_givers.js` (givers, talk, pools, drops) and `quest_npcs.js`
(characters, encounters, timed challenges).

## Progress

Quest progress is solo: everyone has their own. FTB Teams is only installed because FTB Quests needs it; claims and
parties stay with Open Parties and Claims.
