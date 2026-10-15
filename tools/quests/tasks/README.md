# Quest writing tasks

The quest plan (`src/plans/quests/`, 878 quests) is written into the book in tasks small enough for one session.
Each task turns a slice of the plan into finished quests: chapter files, dialogue, rewards, checked and committed.

**For Dylan:** start a session (Sonnet is fine), and say: `Do quest tasks T11 to T14 from tools/quests/tasks/README.md`
(a session can do several tasks in a row, one commit each). Do them in order, one session at a time (they all touch the
same generated files). An Opus session reviews and deploys each wave when it's done. Everything below this line is for the
model doing the task. Reading the task table is spoiler-free; the plan files and `src/plans/followups.md` are not.

---

## The brief (every task)

You are writing quests for a Forge 1.20.1 modpack's FTB Quests book. The pack owner (Dylan) **plays these quests
unspoiled**: never show him quest titles, plots, steps or dialogue. Your report to him is counts, mechanics and
characters only (see "Report" below).

### Read first

1. `tools/quests/README.md`: the chapter format, every task, reward and giver type the generator supports, and what
   counts when. **Only use what it lists.**
2. `tools/quests/src/plans/quests/README.md`: the design rules the owner set (pacing, givers, timed challenges,
   protection, fishing competitions, tiers, shared anchors).
3. The plan file for your chapter: `tools/quests/src/plans/quests/<chapter>.json`. Its header (`line`, `giver`,
   `feel`) sets the tone; each entry is one quest with `id`, `title`, `tier`, `types`, `after`, `summary`, `mods`,
   `landmarks`, `reward`.
4. `tools/quests/src/authoring/common.py` (the helpers) and one finished chapter as a style model:
   `src/authoring/skill_mining.py` (organisation givers, encounters), `skill_fishing.py` (characters, prize fish),
   `small_favours.py` (a favour chain). Match their density and tone.
5. `tools/quests/src/pack.json`: `organisations` and `characters`. **Every character has a `personality`; write
   their lines in that voice.** Read the whole cast: characters mention each other (Hale's crush on Marta, Pip
   borrowing Orrin's books, Nell bossing Hesk).

### Write

- One authoring file per chapter: `tools/quests/src/authoring/<chapter>.py`. If it exists, **append** your quests to
  it and leave existing quests untouched (ids, task order and text: changing them resets players' progress). If it
  doesn't, create it like the others: a docstring naming the plan file, a `Q = [...]` list, and a `chapter(...)` call
  using the group and order from the table below.
- Write exactly the plan entries in your task's slice (by chapter and `tier`), in plan order, with the plan's `id` as
  the quest id and its `after` links. Keep each quest faithful to its `summary` and `reward`; you may refine wording
  and details, not the plot.
- **Ids** must exist: items, mobs, biomes, structures, advancements in `tools/quests/registry.json`. The check gives
  "did you mean" suggestions. Never invent an id.
- **Text**: a short `text` (1 to 3 sentences) setting the scene, plainly written, British spelling (armour, colour).
  Every task and quest title readable at a glance.
- **Where characters are**: a character with a `home` in pack.json lives there, not in Reece; send players there and describe it that way.
- **Dialogue: short and plain** (Dylan and Fionah found the early quests too wordy). 1 line per talk step, giver,
  encounter or thanks, 2 at most; each line under 15 words. Say what matters (what's wrong, what they want) and stop.
  Personality comes through word choice, not length: Dagna's "Aye", Maren's "dearie", one Bram exclamation, not a
  speech. No filler, no repeating the quest text, no jokes stacked on jokes. Organisation representatives
  (`talk_org`, `giver_org`) are ordinary villagers: plain, friendly, brief. The quest checker enforces the limits.
- **Rewards**: every skill-path quest gives that skill's XP (trees: `mining forage farm fish cook craft attack range
  defense agility magic taming`); other chapters give the XP of the skill the quest exercises. Scale by tier:

  | tier | skill XP | | tier | skill XP |
  |---|---|---|---|---|
  | start | 15-40 | | act3 | 250-600 |
  | prologue | 30-150 | | act4 | 400-800 |
  | act1 | 80-300 | | act5 | 600-1000 |
  | act2 | 150-400 | | post | 1000-1500 |

  `any`-tier quests: by effort, 50-300. Chain endings and boss quests sit at the top of their tier. Artifacts
  (`artifacts:*`) only as the reward of the quest whose plan entry has them, with `signature` set (see
  `src/plans/artifact_quests.md`).

- **Item rewards should feel like something** (Dylan, 2026-10-15). A few items or pieces of gear per quest is fine.
  - **Prefer, in order:** ingredients for something cool (Ars source gems, Iron's arcane essence, upgrade orbs and
    runes, Cataclysm ingots and smithing templates, Tinkers' alloys, rare mob drops); enchanted books (one strong or
    themed enchantment, e.g. `{"item": "minecraft:enchanted_book", "enchant": {"minecraft:mending": 1}}`); modded
    weapons, armour and tools (Spartan Weaponry, Spartan Shields, Iron's, Cataclysm, Twilight, Aquaculture).
    Giving what someone needs to craft the cool thing beats giving the cool thing.
  - **Avoid** plain or enchanted vanilla weapons, armour and tools (iron sword, leather boots, diamond pickaxe): they
    have no flavour. The checker warns on them. Fine as a starter in the `start`/`prologue` tiers.
  - **Choice rewards** where players' styles differ (a fighter, a mage, a builder): `{"choice": [{"item": ...},
    {"item": ...}], "title": "Choose one"}`, two to four options, each with the usual item fields. Each player picks
    one. Good for chain endings and boss quests.
  - **Capstones and finales** (a skill path's last quest, a chapter's final boss) give a unique relic: named,
    `"unbreakable": true`, enchanted, with lore, on a modded base where one fits
    (`{"item": ..., "name": ..., "lore": [...], "enchant": {...}, "unbreakable": true}`), or a choice of relics.
    The main story's finale (`main_story:epilogue`, table `forest_relics`) is the model.
  - Keepsakes (a named banner, a journal) are fine alongside a real reward, never instead of one.

### Design rules (the owner's, non-negotiable)

- **Build on what's really there.** Before writing a puzzle or interaction at a structure, look it up in
  `tools/quests/src/structure_contents.json` (what blocks and entities its pieces actually contain). Never invent
  levers, bells, altars, portraits or mosaics a structure doesn't have. Use what it has: `use` its bells, levers,
  buttons, candles or campfires; `search` its chests and barrels for the quest's items; or have the player bring and
  place what's missing (a `build`). The list says what a structure *can* contain; the reviewer then checks your puzzles against real generated copies
  (`verify_puzzles.py`), so keep counts modest (needing 3 of something the list shows in many pieces is safe; needing
  1 of something in a single piece may fail). If a structure says `"pieces": 0`, its contents are unknown: stick to `search`
  (nearly every structure has containers), `spawn` fights and `observe`.
- **Every quest and every step has an in-world reason.** Someone wants it, something is wrong, something changes
  because you did it. Never a bare count ("cast 20 spells", "kill 15 zombies"): say who needs it and why ("the dead
  won't stay down; only fire lays them to rest: burn twenty"), and make the step title say it in-world too. Odd jobs
  can have silly reasons, but they still have one.
- **Magic has many schools; use them.** Different quests should lean on different Iron's Spells schools (fire,
  ice, lightning, holy, ender, blood, evocation, nature, eldritch) where the story fits: holy against the undead, ice
  for a fire that needs putting out, nature for a blighted grove. `spellkill` (kills landed by a school) and `cast`
  (a spell or a school) make that real.
- **Finish where you are.** A quest completes at its objective (follow the map, get the loot, done). No routine walk
  back to an NPC. Returning to a giver is right at the end of a chain, or mid-chain when they then send you somewhere
  different. Never "go to X, back to the village, back to X": do the business at X in one trip. Mid-chain news can
  come by an encounter (the character turns up) instead of a trip home.
- **Quests are a pathway, never a gate.** Boss and mob quests ask for the `kill` (only counts while the quest is open),
  not the boss's drop or advancement.
- **Fishing competitions aren't timed**: a `drop` task with `"from": ["fishing"]` (a prize fish).
- **Reece** sits on a lake (no river). Its people and where they stand: `src/npc_positions.json`.
- **Disabled content:** Alex's Caves' Magnetic Caves and Toxic Caves are off; never use them.
- **Stats look back.** A plain `stat` task reads the lifetime total, so it's done at once for anyone who has done
  that thing before. Use a stat only as a `timed` goal (it counts from the start) or for a true milestone.
- **Build tasks count only blocks placed during the step**, so don't worry about what's already standing nearby.
- Variety matters: the plan's `types` say what kind of quest it is; keep that kind.

### When the engine can't do it yet

Puzzle blocks and timed-challenge restrictions **are** supported: give a puzzle quest a `protect` for exactly the
blocks the puzzle depends on (never whole buildings), and a timed challenge the `no` list its plan entry implies
(a race: `teleport` and usually `mounts`; a climb: `elytra` or `pearls` as the summary says). Grappling hooks are
always allowed: never ban them, even where a plan summary says to. Use them
rather than logging them.

Also supported (see `tools/quests/README.md`): **escorts** (encounter `"then": "escort"` with `"to"`),
**stealth** (a `timed` goal to a place or structure with `"no": ["hurt"]`), **defending a spot** (a `timed` `hold` goal,
usually with `waves`), **building** (a `build` task), **puzzles players change** (`protect` with `"reset_minutes"`),
and **character shops** (give the character at the end of each chain one or two themed deals in pack.json).

Runs and deliveries are a `timed` goal to a `structure` or `place` with `"away"` (distance from the start), never a sprint stat. Attuning waystones is a `waystones` task: use `"total": true` unless the step makes a new one (lighting a waystone the player placed), or players who already have waystones get stuck. Quest mobs spawn a distance away and act as their kind does (prey runs, fighters fight); named targets (kill encounters) come tougher and bigger by default; spawn waves are normal strength, so only give a wave a `boost` when the story says these ones are special, and make a legendary target bigger still. A fight the quest sends you to is a `kill` with `"spawn"`, and a boss kill always has `"spawn"` with `"ensure": true` (so the boss is there even if someone beat it first) (the enemies come when you arrive; not in villages, where they would kill villagers). Spellcasting is a `cast` task (Iron's Spells is the only magic mod; there is no Ars Nouveau). Taming and breeding have their own tasks (`tame`, `breed`); use them, never a checkmark or the generic tame advancement. Photos are supported too: a `photo` task (Camerapture camera; reward the camera, `camerapture:camera`, in the first
photo quest). Some plan entries may still need mechanics the generator doesn't have: anything the README doesn't list. **Write the quest anyway** with the nearest supported tasks (a
`checkmark` for "solve the puzzle", a `kill` count for a defence, an `observe` or `structure` for "find it"), so the
chain stays whole and playable. Then add one line per quest to `tools/quests/src/plans/followups.md` under "Engine needed":
`- <chapter>:<id>: needs <mechanic>; written as <what you used>`.

If an `after` link points to a quest that isn't written yet (another chapter's later task), leave the link out and add
`- <chapter>:<id>: restore after <target>` under "Links to restore" in the same file. Never drop a link to a quest
that already exists.

### New characters

The Reece cast is in `pack.json`; use them, never rename them. If your slice needs a character who isn't there (an
encounter-only stranger, a quest-specific villager), add them to `characters` with `name`, `entity`/`profession`,
`personality` (one or two sentences), 4 `idle` lines and 2 `hail` lines (what they call out when they have something for the player), each under 12 words, and list them in your report so Dylan can adjust names
and personalities. Characters who live in Reece need placing in game: say so in the report (Dylan places them with
`/questnpc place <id>`).

### Check

From `tools/quests`:

```
python src/authoring/<chapter>.py        # for each chapter you touched
python make_quests.py                    # checks everything, then writes the book and scripts
python coverage.py --check               # the plan still lines up
```

Fix every error. Warnings about artifacts given without a signature must be fixed too. Re-run until both pass. Then
run the quest checker on the chapters you touched, and fix what it finds:

```
python lint_quests.py <chapter> [<chapter> ...]
```

Errors must be fixed. Warnings must be fixed, or (only when no task in the README can do it) logged in
`src/plans/followups.md` and mentioned in your report. Then look at your diff once more against the design rules above.

**Puzzle check** (if your slice has `use` or `search` steps at structures). Once per session, after the session's
last task is written (not after each task), from `pack/`:

```
python tools/quests/verify_puzzles.py --chapters <chapter>,<chapter>
```

It remembers what it has already checked, so it only generates structures for new puzzle steps (and finishes at once
when there are none). When it does need the test server it starts and stops it itself, but only if nobody is on the
live server; if someone is, it says so and checks nothing: say so in your report. It writes
`tools/quests/src/plans/puzzle_check.md`. Any step marked SHORT or NOT FOUND must change: lower the count to what every
copy had, switch to `search`, or have the player bring and place the block first (a `build` step before the `use`).
Re-run until every step is OK, then commit the fixes (and `puzzle_cache.json`) with the last task.

### Commit

One commit per task. Run `python tools/quests/make_quests.py` once more right before committing (the book in
`config/ftbquests/` must match your last edit; two passes committed a stale book), then from the repo root (`pack/`):
`packwiz refresh`, and commit everything (authoring files, `src/chapters/`,
`config/ftbquests/`, the generated KubeJS files, `pack.json`, `followups.md`, this README's progress table) with a
message like `Quests T07: discovery_land, 35 quests`, and push to `main`. Don't deploy to the live server and don't
restart anything; Dylan or an Opus session does that.

### Report

Fill in your task's row in the progress table below, then tell Dylan, spoiler-free:
- how many quests you wrote, per chapter;
- which kinds (counts by plan `types`, e.g. "6 exploration, 4 crafting, 2 timed");
- new characters (name, where they appear in general terms like "an encounter in the Nether", personality line);
- how many follow-ups you logged (engine needed / links to restore), without saying which quests;
- the quest checker's final counts, and whether the puzzle check ran (and passed) or was skipped;
- the commit hash.

When a session does several tasks, finish and commit each one (checker, puzzle check, progress row) before starting
the next, and give one combined report at the end.

---

## Chapters

| chapter | group | order | | chapter | group | order |
|---|---|---|---|---|---|---|
| `main_story` | story | 0 | | `skill_taming` | skills | 11 |
| `milestones` | milestones | 0 | | `twilight` | realms | 0 |
| `skill_mining` | skills | 0 | | `alexs_caves` | realms | 1 |
| `skill_farming` | skills | 1 | | `nether` | realms | 2 |
| `skill_fishing` | skills | 2 | | `end` | realms | 3 |
| `skill_cooking` | skills | 3 | | `small_favours` | side | 0 |
| `skill_foraging` | skills | 4 | | `odd_jobs` | side | 1 |
| `skill_crafting` | skills | 5 | | `village_errands` | side | 2 |
| `skill_attack` | skills | 6 | | `discovery_land` | explore | 0 |
| `skill_range` | skills | 7 | | `discovery_sea` | explore | 1 |
| `skill_defense` | skills | 8 | | `discovery_sky_and_underground` | explore | 2 |
| `skill_agility` | skills | 9 | | | | |
| `magic` | skills | 10 | | | | |

## Tasks

Waves follow the game's tiers, so each wave is playable before the next is written. In each wave, do the main story
task first (T11, T18, T25, T28): other chapters link to its anchors. Counts are the plan entries in the slice.

| task | wave | quests | slice (chapter, tiers, count) |
|---|---|---|---|
| T01 | 1 | 18 | `skill_attack` (start to act1, 10); `skill_defense` (start to act1, 8) |
| T02 | 1 | 23 | `skill_range` (start to act1, 10); `skill_taming` (start to act1, 13) |
| T03 | 1 | 26 | `skill_agility` (start to act1, 14); `skill_crafting` (start to act1, 12) |
| T04 | 1 | 22 | `magic` (start to act1, 16); `small_favours` (start to act1, 6) |
| T05 | 1 | 32 | `village_errands` (all, 32) |
| T06 | 1 | 24 | `milestones` (all, 24) |
| T07 | 1 | 35 | `discovery_land` (every tier except any, 35) |
| T08 | 1 | 46 | `discovery_land` (any, 46) |
| T09 | 1 | 22 | `discovery_sea` (all, 22) |
| T10 | 1 | 23 | `discovery_sky_and_underground` (all, 23) |
| TD | 2 | 0 | **Do this first.** Rewrite all existing dialogue short (see "Task TD" below) |
| TF | - | 0 | Upgrade the logged stand-ins to real tasks (see "Task TF" below) |
| TF1 | - | 0 | Task TF for only: `alexs_caves`, `discovery_land`, `discovery_sea`, `discovery_sky_and_underground`, `end`, `magic` |
| TF2 | - | 0 | Task TF for only: `main_story`, `milestones`, `nether`, `skill_agility`, `skill_attack`, `skill_cooking` |
| TF3 | - | 0 | Task TF for only: `skill_crafting`, `skill_defense`, `skill_farming`, `skill_fishing`, `skill_foraging`, `skill_mining`, `skill_range` |
| TF4 | - | 0 | Task TF for only: `skill_taming`, `small_favours`, `twilight`, `village_errands` |
| TR1 | - | 0 | Task TR for only: `main_story`, `milestones`, `start`, `alexs_caves`, `twilight`, `nether`, `end` |
| TR2 | - | 0 | Task TR for only: `skill_attack`, `skill_defense`, `skill_range`, `skill_taming`, `skill_agility`, `skill_crafting`, `magic` |
| TR3 | - | 0 | Task TR for only: `skill_cooking`, `skill_farming`, `skill_fishing`, `skill_foraging`, `skill_mining` |
| TR4 | - | 0 | Task TR for only: `discovery_land`, `discovery_sea`, `discovery_sky_and_underground`, `small_favours`, `odd_jobs`, `village_errands` |
| TK | - | 0 | Real rewards beside keepsakes, every chapter (see "Task TK" below) |
| T11 | 2 | 17 | `main_story` (act2, 17) |
| T12 | 2 | 29 | `skill_attack` (act2, 7); `skill_defense` (act2, 8); `skill_range` (act2, 7); `skill_taming` (act2, 7) |
| T13 | 2 | 33 | `skill_agility` (act2, 7); `skill_crafting` (act2, 10); `magic` (act2, 16) |
| T14 | 2 | 26 | `skill_cooking` (act2, 8); `skill_farming` (act2, 9); `skill_fishing` (act2, 9) |
| T15 | 2 | 19 | `skill_foraging` (act2, 9); `skill_mining` (act2, 10) |
| T16 | 2 | 26 | `twilight` (act2, 26) |
| T17 | 2 | 36 | `alexs_caves` (act2, 36) |
| T18 | 3 | 20 | `main_story` (act3, 15); `small_favours` (act3, 5) |
| T19 | 3 | 39 | `nether` (act3 and any, 39) |
| T20 | 3 | 18 | `twilight` (act3, 18) |
| T21 | 3 | 14 | `alexs_caves` (act3, act4 and any, 14) |
| T22 | 3 | 21 | `skill_attack` (act3, 5); `skill_defense` (act3, 6); `skill_range` (act3, 4); `skill_taming` (act3, 6) |
| T23 | 3 | 20 | `skill_agility` (act3, 6); `skill_crafting` (act3, 5); `magic` (act3, 9) |
| T24 | 3 | 20 | `skill_cooking` (act3, 4); `skill_farming` (act3, 2); `skill_fishing` (act3 and any, 7); `skill_foraging` (act3, 3); `skill_mining` (act3, 4) |
| T25 | 4 | 23 | `main_story` (act4, 10); `twilight` (act4, 10); `nether` (act4 and act5, 3) |
| T26 | 4 | 31 | `end` (all, 31) |
| T27 | 4 | 38 | act4 of every skill path: `skill_attack` 3, `skill_defense` 2, `skill_range` 4, `skill_taming` 4, `skill_agility` 4, `skill_crafting` 3, `magic` 5, `skill_cooking` 3, `skill_farming` 2, `skill_fishing` 3, `skill_foraging` 2, `skill_mining` 3 |
| T28 | 5 | 27 | `main_story` (act5, 27) |
| T29 | 5 | 31 | act5 and post of every skill path: `skill_attack` 3, `skill_defense` 3, `skill_range` 3, `skill_taming` 2, `skill_agility` 2, `skill_crafting` 2, `magic` 5, `skill_cooking` 2, `skill_farming` 3, `skill_fishing` 2, `skill_foraging` 2, `skill_mining` 2 |

Total 759 (with the 119 already written, the plan's 878).

## Task TF: upgrade the stand-ins

(The first TF pass ran out of room after 13 lines; TF1 to TF4 split the rest by chapter, one session each. Check every
line in your chapters: for example, `interact` covers giving a wolf a collar or feeding a mob, `make` covers brewing
or cooking something specific, `be` covers storms, sunsets and riding, `mine` covers harvesting.)

`src/plans/followups.md` lists ~300 quests written with a stand-in because the engine couldn't do something at the
time. Many can now be done properly: the README's task list has grown a lot since they were written (`use`, `search`,
`mine`, `build`, `tame`, `breed`, `cast`, `spellkill`, `photo`, `waystones`, `skill_level`, `stats`, `be` with
weather/time/riding, `biomes`, `make`, `trade`, `sleep`, `interact`, `spawn`, timed `structure`/`hold`/`away` goals,
escorts). Go through every line under "Engine needed", chapter by chapter:

- Open the quest. If one or more README tasks can now do what the line says the quest needs, faithfully, rewrite
  those steps (keep the quest's id, story and rewards; replacing a stand-in task in place is fine) and delete the
  line from followups.md.
- If nothing can, leave the line. Don't force a weak substitute just to clear a line.
- Puzzles still follow "Build on what's really there" (check `src/structure_contents.json`).
- Dialogue you touch follows the short-dialogue rules.

After each chapter: rebuild it, `python make_quests.py`, `python lint_quests.py <chapter>`. At the end:
`python coverage.py --check`, one puzzle check (`python tools/quests/verify_puzzles.py`), and commit per chapter group
(`Quests TF: stand-ins upgraded in <chapters>`). Report how many lines you cleared and how many remain, and the most
common remaining needs (so the engine can grow next).

## Task TR: richer rewards

Dylan wants rewards with more flavour (see "Item rewards should feel like something" in the brief). Go through every
quest in your chapters and improve the item rewards where they're flat. Skill XP stays exactly as it is, and so do
ids, tasks, text and dialogue.

- **Replace** vanilla weapons, armour and tools past the first tiers (the checker lists them as "vanilla gear
  reward") and other flat rewards (a stack of iron, a vanilla tool, plain bread at act3) with ingredients for something
  cool, an enchanted book that suits the quest, or modded gear, all fitting the quest's story and tier. A quest about
  a smith gives a smith's things; a quest about a mage gives arcane things.
- **Keep** what already fits: themed modded items, artifacts with their signature, shop deals, keepsakes beside a
  real reward. Don't touch a reward just to touch it.
- **Choice rewards:** give chain endings and boss quests a `choice` of 2-4 options suited to different players
  (fighter, mage, builder or farmer) where it fits. Aim for a few per chapter, not every quest.
- **Capstones** (each skill path's last quest, each realm chapter's final boss): a unique unbreakable named relic on a
  modded base where one fits, or a choice of relics. Don't change `main_story:epilogue` (already done).
- Every item must exist in `registry.json` and not be in its `trimmed` list. Don't give the same reward item in
  every quest of a chapter: vary them.
- Match the tier: act1 gets iron-level things and early ingredients; act4 and up get endgame materials (Cataclysm
  ingots, legendary ink, netherite).

After each chapter: rebuild it, `python make_quests.py`, `python lint_quests.py <chapter>` until there are no
"vanilla gear reward" warnings. At the end: `python coverage.py --check`, then one commit per task
(`Quests TR1: richer rewards in <chapters>`), pushed. Report, spoiler-free: how many quests' rewards changed per
chapter, how many choice rewards and relics you added, and the commit hash.

## Task TK: real rewards beside keepsakes

`python lint_quests.py` lists every quest whose only item rewards are keepsakes ("only keepsake rewards": a named
journal, banner, bone or bell, a spyglass, a map). Keep the keepsake (it's part of the story) and add one real
reward beside it, by the rules in "Item rewards should feel like something": ingredients for something cool, a
fitting enchanted book, or modded gear, matched to the quest's story and tier. Plain spyglasses and maps in later
tiers may be swapped for the real reward instead. Vary the rewards; don't give every journal quest the same book.
Change nothing else (ids, tasks, text, dialogue and skill XP stay as they are). Rebuild each chapter you touch, then
`python make_quests.py` and `python lint_quests.py` until no "only keepsake rewards" warnings remain, and
`python coverage.py --check`. One commit, `Quests TK: real rewards beside keepsakes`, pushed. Report, spoiler-free:
how many quests changed per chapter, and the commit hash.

## Task TD: shorten the dialogue

Dylan and Fionah found the dialogue too much. Rewrite every line of dialogue already written to the rules above (1
line, 2 at most, each under 15 words), across every authoring file in `src/authoring/` (giver lines, talk lines,
encounter lines and thanks, timed-challenge lines) and every character's `idle` (keep 4) and `hail` (keep 2) lines in
`src/pack.json` (under 12 words each). Keep each character's voice and what each line has to say (the instruction,
the clue, the twist); cut everything else. Don't change anything that isn't a dialogue line: ids, tasks, task order,
rewards and quest text stay exactly as they are. Rebuild every chapter, then run `python make_quests.py`,
`python coverage.py --check` and `python lint_quests.py` until there are no dialogue errors or warnings. One commit:
`Quests TD: dialogue shortened`.

## Progress

| task | done | quests | follow-ups | commit |
|---|---|---|---|---|
| T01 | yes | 18 | 5 engine, 0 links | `Quests T01` in git log |
| T02 | yes | 23 | 11 engine, 0 links | `Quests T02` in git log |
| T03 | yes | 26 | 16 engine, 0 links | `Quests T03` in git log |
| T04 | yes | 22 | 11 engine, 0 links | `Quests T04` in git log |
| T05 | yes | 32 | 9 engine, 0 links | `Quests T05` in git log |
| T06 | yes | 24 | 6 engine, 0 links | `Quests T06` in git log |
| T07 | yes | 35 | 17 engine, 1 link | `Quests T07` in git log |
| T08 | yes | 46 | 16 engine, 0 links | `Quests T08` in git log |
| T09 | yes | 22 | 11 engine, 1 link | `Quests T09` in git log |
| T10 | yes | 23 | 7 engine, 0 links | `Quests T10` in git log |
| TD | yes | 0 | 0 | `Quests TD` in git log |
| T11 | yes | 17 | 3 engine, 0 links | `Quests T11` in git log |
| T12 | yes | 29 | 15 engine, 0 links | `Quests T12` in git log |
| T13 | yes | 33 | 15 engine, 0 links | `Quests T13` in git log |
| T14 | yes | 26 | 13 engine, 0 links | `Quests T14` in git log |
| T15 | yes | 19 | 10 engine, 0 links | `Quests T15` in git log |
| T16 | yes | 26 | 11 engine, 0 links | `Quests T16` in git log |
| T17 | yes | 36 | 12 engine, 0 links | `Quests T17` in git log |
| T18 | yes | 20 | 11 engine, 0 links | `Quests T18` in git log |
| T19 | yes | 39 | 14 engine, 0 links | `Quests T19` in git log |
| T20 | yes | 18 | 7 engine, 0 links | `Quests T20` in git log |
| T21 | yes | 14 | 9 engine, 0 links | `Quests T21` in git log |
| T22 | yes | 21 | 11 engine, 0 links | `Quests T22` in git log |
| T23 | yes | 20 | 14 engine, 0 links | `Quests T23` in git log |
| T24 | yes | 20 | 17 engine, 0 links | `Quests T24` in git log |
| T25 | yes | 23 | 10 engine, 1 link | `Quests T25` in git log |
| T26 | yes | 31 | 15 engine, 1 link | `Quests T26` in git log |
| T27 | yes | 38 | 19 engine, 0 links | `Quests T27` in git log |
| T28 | yes | 27 | 7 engine, 0 links (3 restored) | `Quests T28` in git log |
| T29 | yes | 31 | 15 engine, 0 links | `Quests T29` in git log |
| TF | partial | 0 | 13 lines cleared, 281 remain | `Quests TF` in git log |
