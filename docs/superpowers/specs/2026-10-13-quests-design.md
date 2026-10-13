# Quests: framework design

Status: framework built on branch `claude/cloud-session-setup-epiuzy`, with a few sample quests. The real content
(story, side quests, milestones, showcases) is still to be written. How to write quests: `tools/quests/README.md`.

## Decisions (from chat, 2026-10-13)

- **Quest mod:** FTB Quests 2001.4.22, plus FTB Teams 2001.3.2 (required) and FTB XMod Compat 2.1.3 (KubeJS hooks for
  later scripting). All CurseForge, both sides. FTB Library (already in the pack for FTB Ultimine) and Architectury
  cover their other dependencies.
- **Authoring:** quests are written as JSON in `tools/quests/src` and generated into FTB Quests' files by
  `tools/quests/make_quests.py`, which checks every id against a snapshot of the pack (`registry.json`). No in-game
  editing: the generator owns `config/ftbquests/quests`.
- **Kinds of quests:** basic intro quests first, a major plot-driven story line, side quests, and quests given by
  NPCs (villagers, mobs) and item drops. Milestones, mod showcases and exploration/collecting chapters too.
- **Rewards:** a variety: items and random reward tables, cosmetics, Pufferfish skill XP in the matching tree, and
  vanilla XP.
- **Progress:** solo. FTB Teams is installed but its parties aren't used, so OPAC stays the only party system.

## How it fits together

| Piece | Where | What it does |
|---|---|---|
| Sources | `tools/quests/src/` | `pack.json` (title, groups), `chapters/*.json`, `reward_tables/*.json` |
| Registry snapshot | `tools/quests/registry.json` | Items, mobs, biomes, structures, advancements, dimensions in the pack, plus trimmed items. Rebuilt by `make_registry.py` from the pack's jars |
| Generator | `tools/quests/make_quests.py` | Checks, then writes the book (`config/ftbquests/quests/`) and two KubeJS data files |
| Quest items | `kubejs/startup_scripts/quest_items.generated.js` | Letters, notes and keepsakes that start quests (`kubejs:quest_*`) |
| Givers data | `kubejs/server_scripts/quest_givers.generated.js` | Who gives which quest, and the "talk to" steps |
| Givers behaviour | `kubejs/server_scripts/quest_givers.js` | Sneak + right-click villagers/mobs for dialogue and a clickable [Accept]; quest item drops; reading quest items; `/quest accept` |

Mechanics:
- **Stable ids.** FTB Quests ids are hashes of chapter file name + quest id + task/reward position, so regenerating
  keeps progress. Renaming or reordering resets that quest's progress.
- **Givers.** A quest with a giver gets a hidden first task waiting for the stage `fq.<chapter>.<quest>` and stays
  invisible until that task is done (`invisible_until_tasks: 1`). Accepting the giver's offer adds that stage.
- **Stages are player tags.** FTB Library's built-in stage provider reads vanilla entity tags, so no extra stage
  mod is needed. After adding a tag, the script calls FTB Quests' `StageTask.checkStages(player)` so the task
  completes at once.
- **"Talk to" tasks** add `fq.<chapter>.<quest>.talk<n>` when the player talks to the right villager or mob while on
  the quest.
- **Requirements across quests.** A giver's `requires` adds an invisible, auto-claimed stage reward
  `fq.<chapter>.<quest>.done` to the required quest, which the script checks before offering.
- **Skill XP.** Rewards run `/puffish_skills experience add {p} puffish_skills:<tree> <xp>` as the server, titled
  like "+150 Farming XP" with the tree's icon.

## Tested (cloud session)

- [x] On a server built from main's current pack (169 server-side mods) plus the three FTB mods, the generated
  sample book loads: "7 chapter groups, 3 chapters, 12 quests, 2 reward tables" (FTB adds a default group).
- [x] All 26 KubeJS server scripts and 6 startup scripts load with 0 errors (including both quest scripts and the
  generated quest item).
- [x] The skill XP command parses (`puffish_skills experience add @a puffish_skills:farm 10`).
- [x] The checker rejects bad sources: unknown/trimmed ids with suggestions, missing namespaces, duplicate quest
  ids, unknown groups, skills, reward tables and `after` links, empty quests and incomplete givers.
- [ ] **In game (needs a player):** the book opens and looks right; claiming each reward kind works; sneak +
  right-click a farmer after "Neighbours" offers the wheat quest and [Accept] adds it; a cleric completes the
  lost-letter "talk" step; zombies drop the Water-Stained Letter and reading it offers the quest.

## Story: proposed structure (to decide together)

The story is a chain of chapters in the "The Story" group, one act per stage of the pack, so it doubles as the
progression spine:

| Act | Pack stage | Story beat (placeholder) |
|---|---|---|
| Prologue | First days, first village | The forest has gone quiet; a village cleric explains the old spirits are asleep |
| Act 1 | Iron, farming, first magic (Iron's Spells) | Wake the first grove: gather what "remembers" the spirits, meet recurring NPCs |
| Act 2 | Deep caves, Alex's Caves, first bosses | Something below is draining the groves |
| Act 3 | The Nether | Follow the trail into the Nether |
| Act 4 | Twilight Forest / the End | The source, the final bosses, the forest wakes |

Recurring characters can be villagers of a given profession, or name-tagged NPCs (`"type": "entity"` with
`"named"`). Story chapters lean on givers and "talk to" steps so the plot is told by people in the world, with the
book as the journal. Side quests from villagers, mobs and drops live in their own chapters, like the samples.

## Next steps

1. Decide the story outline and cast.
2. Write the Getting Started chapter properly (the sample is a start), then the milestones spine.
3. Side-quest chapters per profession and drop quests.
4. Mod showcase and exploration chapters.
5. In-game test pass; then deploy (FTB mods + config + KubeJS) and `/ftbquests reload`.
