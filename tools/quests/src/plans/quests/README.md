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
  `src/mod_roles.json`).
- **Landmarks**: many are involved in quests, but they don't each need a dedicated quest. A quest of its own is for
  a place with a real story, puzzle or fight; small places (lookouts, lone chests, shrines, cellars) are settings
  inside bigger quests or simply places to find. Coverage is not a target.
- **Pacing: finish where you are.** Most quests complete at the objective: follow the map, get the loot, done;
  no walk back to an NPC. A giver hands out the first quest of a chain and the rest open in the book as each step
  finishes. Returning to a giver is good **at the end of a chain** (the payoff, the next chain) and **mid-chain when
  they then send you somewhere different** (new information, a change of plans). What to avoid is **leaving a
  place only to come straight back to it** (out to X, back to the village, out to X again): do the business at X
  in one trip. Mid-chain news can also reach the player in the field:
  a letter by mail, or the character turning up. "Bring it back" stays where delivering is the point (couriers,
  village errands).
- **Small favours** (`small_favours.json`): One Small Favour-style chains where each favour needs another first;
  every step goes somewhere new, and the chain unwinds back to whoever started it.
- **Fishing competitions aren't timed**: you fish until you land the competition's quest item (a prize fish that
  can only be caught while the quest is open). Needs a fishing version of the `drop` task.
- **Timed challenges** can switch off shortcuts for their duration where they'd trivialise the challenge:
  waystone and warp-scroll teleports, riding mounts, and per challenge other movement (elytra/wings, ender
  pearls). Each timed quest says which. Grappling hooks are always allowed (Dylan, 2026-10-14).
- **Protecting objectives: specific blocks, not areas.** The blocks a puzzle or quest depends on (braziers,
  levers, altars, a monument's pieces) can't be broken, blown up or pushed by pistons; everything around them stays
  normal survival. Clever solutions are welcome (any route, tool or trick that works), just not breaking the
  puzzle. Anything a quest changes resets for the next player. Named characters and givers can't be hurt, don't
  despawn or convert, and respawn at their spot if lost; Reece itself is a server claim. Structure loot is per player
  (Lootr), quest items drop only for the player on the quest, and progress is per player or FTB team.
- **Odd jobs and nonsense** (`odd_jobs.json`): deliberately pointless standalone quests with token rewards.

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
