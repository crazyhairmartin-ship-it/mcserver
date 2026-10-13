# The quest list (SPOILERS in the .json files)

Every quest the pack will have, one entry each, before it's written in full into `src/chapters/`. The pack owner
plays unspoiled: summaries of this list for them give counts and coverage only (`docs/quest-coverage.md`), never
titles, plots or steps. Format: see the docstring of `tools/quests/coverage.py`. Check with
`python3 tools/quests/coverage.py --check` (and `--gaps` for what's still uncovered).

## What the owner decided (design: `docs/superpowers/specs/2026-10-13-boss-progression.md`)

- **Quests are a pathway, never a gate.** Anyone can find and kill any boss without quests; the quest gives
  direction and helpful bonuses. Quest progress unlocks later quests; a boss killed while its quest isn't open
  doesn't complete it.
- **Main story** (Prologue, Acts I-V) with branches out to other content. **Ignis is the final boss**. Mowzie's
  bosses are woven in (Act I-II). The Cataclysm bosses are post-Dragon (Act V), in the owner's order hardest last:
  Netherite Monstrosity, Ender Guardian, Harbinger, Scylla, Ancient Remnant, Leviathan, Maledictus, Ignis.
- **Realms branch off as their own questlines** (Twilight Forest, Alex's Caves, Nether, End) while showing where
  they sit in the story (tiers).
- **Magic questline** (Iron's Spells) runs alongside, ending with **Echo of Tyros**.
- **Skill paths**, one per Pufferfish skill, each with its own story and feel, given by an organisation:
  Mining (Miners' guild: rescues), Foraging (Herbalists), Farming (Growers' co-op: harvest festival), Fishing
  (Anglers' society: competitions), Cooking (Tavern keepers), Crafting (Crafters' guild), Attack (Bounty office:
  monster hunting), Range (Hunters' lodge: the hunt), Defense (Village watch), Agility (Couriers: deliveries against
  the clock), Magic (Arcane order), Taming (Sanctuary keepers). Every skill quest gives that skill's XP; capstones
  give a unique named, enchanted item.
- **Givers**: organisation representatives (villagers by profession, pooled per organisation), named characters in
  the spawn village **Reece**, and characters who come to the player (encounters). Nearby villages are destinations.
- **Discovery quests** start out in the world: finding an item, a structure or a biome.
- **Artifacts**: almost all are quest rewards, each from one quest designed around it (`"signature"`), which can be
  a step in a chain or a standalone quest. Concepts and placements: `src/plans/artifact_quests.md`.
- **Variety**: not just "kill this boss". Fetch, collect, craft, build, hunt, unique drops, talk, deliver, escort,
  encounter, timed challenges, contests, rescues, puzzles, exploration.
- **Mods**: quests should bring in virtually every content mod (`tools/quests/mods.json`; roles in
  `src/mod_roles.json`). **Landmarks**: not every landmark needs a quest; the coverage report lists those without.

## Tiers (when in the game)

`start` (first hour), `prologue` (wood/stone), `act1` (iron), `act2` (diamond), `act3` (Nether, to netherite),
`act4` (full netherite, the Dragon), `act5` (post-Dragon: Cataclysm), `post` (endgame, Tyros), `any` (no fixed
place: discovery quests, repeatables).

## Shared anchors

Other files may depend on these ids in `main_story.json`: `act1_start`, `act1_finale`, `act2_start`, `act2_finale`,
`act3_start`, `act3_finale`, `act4_start`, `act4_finale`, `act5_start`, `final_boss`; and `start.json`: `welcome`.

## Writing an entry

- `summary`: one or two sentences: the situation, what the player does, the twist if any. Use real things from
  the pack (check ids in `tools/quests/registry.json`).
- `mods`: every mod whose content the quest uses (not libraries). `landmarks`: where it starts or sends the player.
- `reward`: short ("Fishing XP, a Neptunium hook").
- `types`: from the list in `coverage.py`.
