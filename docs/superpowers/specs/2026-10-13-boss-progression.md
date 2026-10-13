# Boss and objective progression (for the story line)

Status: proposal for discussion, 2026-10-13 (revised: Cataclysm's main bosses moved after the Ender Dragon and ordered by the owner's testing; Mowzie's bosses in the main story; Ignis the final boss and Echo of Tyros the magic questline's; compass real lock decided, not built; quests are a pathway with bonuses, not a gate; realm questlines; discovery quests; artifacts as quest rewards). Built from the pack's current mod list on `main` (merged into
`claude/cloud-session-setup-epiuzy`), reading each mod's jar: boss tags, structures and where they generate, locator
recipes, and boss loot tables. Difficulty is relative (from the mods' designs and drops), not measured in game.

## Spoiler policy

The owner wants to play the quests unspoiled, but approve the **approach, difficulty, style and plot**. So when
quest work is shown to the owner (chat, issue comments, summaries): describe structure, mechanics, difficulty
curve, tone and the plot at outline level, and keep specifics vague: no quest names or text, dialogue, exact
rewards, hidden triggers, discovery quest locations or twists, unless the owner asks for one. Plot details that
need approval are offered as a short outline with an explicit "spoiler" warning, so the owner can choose to read
them. Quest sources (`tools/quests/src/`) and the generated book are full spoilers. This design doc covers the
framework and the boss order (public knowledge); story text belongs in the sources, not here.

## What's in the pack

| Mod | Bosses (tagged by the mod) | Where | How you get there |
|---|---|---|---|
| **L_Ender's Cataclysm** 3.31 | Ancient Remnant | Cursed Pyramid (desert) | Desert Eye |
| | Maledictus | Frosted Prison (snowy plains) | Cursed Eye |
| | The Harbinger | Ancient Factory (underground) | Mech Eye |
| | The Leviathan | Sunken City (deep oceans) | Abyss Eye; summoned with the Abyssal Sacrifice (Heart of the Sea, nautilus shells, mineral blocks) |
| | Scylla | Acropolis (warm ocean) | Storm Eye (prismarine, diamond) |
| | Netherite Monstrosity | Soul Black Smith (Nether) | Monstrous Eye (netherite scrap) |
| | Ignis | Burning Arena (nether wastes) | Flame Eye (netherite scrap) |
| | Ender Guardian | Ruined Citadel (End highlands) | Void Eye (shulker shells) |
| | _Mini-bosses:_ Kobolediator, Wadjet (desert), Aptrgangr (Frosted Prison), Coral Golem (Sunken City), Clawdian, Ender Golem | | |
| **Mowzie's Mobs** 1.8.2 (+ **Mowzie's Cataclysm** eyes) | Ferrous Wroughtnaut | Wrought Chamber (underground) | Wrought Eye |
| | Umvuthi | Umvuthana Grove (savanna) | Sun Eye |
| | Frostmaw | Frostmaw spawn (snowy) | Frostmaw Eye |
| | Sculptor | Monastery (tall peak, a climb) | Tongbi Eye |
| **Twilight Forest** 4.3 | Naga → Lich → Minoshroom → Hydra → Knight Phantoms → Ur-Ghast → Alpha Yeti → Snow Queen | Twilight Forest dimension (portal: a diamond into a flower-ringed pool) | Fixed order; each boss lifts the curse on the next area |
| **Iron's Spells** 3.16 | The Dead King | Catacombs (underground) | Find it |
| | Echo of Tyros, First Flamebearer | Summoned (Tyros Statue, crafted with a pyrium ingot; to confirm in game) | Nether tier |
| | _Mini-bosses:_ Ancient Knight (Nether Citadel, Ancient Battleground), Archevoker (Evoker Fort), Necromancer (Catacombs), Pyromancer/Cryomancer towers, Ice Spider den | | |
| **Alex's Caves** 2.0 | Luxtructosaurus | Volcano, Primordial Caves | Summoned with the Ominous Catalyst (heavy bones + amber curiosity) |
| | _Biome bosses/challenges (untagged):_ Hullbreaker (Abyssal Chasm), Forsaken (Forlorn Hollows), Tremorzilla (Toxic Caves, raised from an egg), Candy Cavity | Cave biomes found with Cave Maps | |
| **Alex's Mobs** | Void Worm (untagged) | End only (`voidWormSpawnDimensions = minecraft:the_end`) | Mysterious Worm item |
| **Friends & Foes** | Wildfire (Nether Citadel), Illusioner, Iceologer | Nether / taiga / snowy | |
| **Vanilla** (reworked by YUNG's) | Elder Guardian, Wither, Ender Dragon, Warden, Raids | Better Ocean Monuments, Better Nether Fortresses (skulls), Better End Island, ancient cities, outposts | |

Structure mods without custom bosses, good as milestones between bosses: YUNG's Better Dungeons, Mineshafts, Desert
and Jungle Temples, Witch Huts and Strongholds; When Dungeons Arise; Dungeons & Taverns (Illager Manor, Nether Keep);
Structory, Towns and Towers; Moog's Voyager, Nether, End, Ocean and Soaring structures; Sky Villages.

**Locators.** Every Cataclysm and Mowzie's Cataclysm eye is crafted from an Eye of Ender, so they need a first Nether
trip (blaze powder). The Nether eyes also need netherite scrap, the Void Eye needs shulker shells (End cities), and
the Storm Eye needs prismarine (an ocean monument). Explorer's Compass and Nature's Compass are in the pack too, so
eyes are a convenient path, not a hard lock; the quest line should still point players at the eyes in this order.

**Gear the bosses feed** (Spartan Weaponry: Cataclysm materials): Ancient Metal (Ancient Remnant, Kobolediator,
Wadjet), Black Steel (Aptrgangr), Cursium (Maledictus), Witherite (The Harbinger), Ignitium (Ignis). Cursium and
Ignitium weapons are Netherite smithing upgrades, so they come after netherite. Twilight: Naga scales, Ironwood,
Steeleaf, Knightmetal (Knight Phantoms' stronghold), Fiery (Hydra blood, Ur-Ghast tears), which the Spartan
Twilight add-on turns into weapons. Iron's: the Dead King drops the Necronomicon and Blood Staff, Tyros the
Betrayer Signet and Divine Soulshard.

## Boss strength (base values from each mod's code)

Health and base attack damage as the mods set them (the pack's configs leave Cataclysm's and Iron's multipliers at
1.0; damage scales up on Hard). For comparison: Elder Guardian 80, Ender Dragon 200, Wither 300, Warden 500.

| Boss | Health | Damage | Notes |
|---|---|---|---|
| Ferrous Wroughtnaut | 40 | 30 | Only hurt from behind; a timing fight |
| Lich (TF) | 100 | | |
| Naga, Minoshroom (TF) | 120 | | |
| Wildfire (F&F) | 120 | 8 | |
| Sculptor | 140 | 10 | A climbing challenge more than a fight |
| Umvuthi | 150 | | Spells and followers |
| Knight Phantoms (TF) | 35 each, 6 of them | | |
| Cataclysm mini-bosses | 110-225 | 10-18 | Coral Golem 110, Wadjet / Ender Golem 150, Aptrgangr 160, Kobolediator 180, Clawdian 225 |
| Alpha Yeti, Snow Queen (TF) | 200 | | |
| Frostmaw, Forsaken (AC), Ur-Ghast (TF) | 250 | 10 | |
| Hydra (TF) | 360 | | |
| Hullbreaker (AC) | 400 | 16 | Underwater |
| The Dead King (Iron's) | 500 | 10 | 15 armour |
| Tremorzilla (AC) | 500 | 30 | Raised from an egg, can be tamed |
| **Ender Guardian** | 333 | 16 | Cataclysm |
| **Scylla**, **The Harbinger** | 390 | 18 / 9 | Cataclysm |
| **The Leviathan** | 400 | | Cataclysm |
| **Maledictus** | 420 | 13 | Cataclysm |
| **Ignis**, **Ancient Remnant** | 450 | 14 / 25 | Cataclysm; the wiki rates Ignis the hardest |
| **Netherite Monstrosity** | 600 | 25 | Cataclysm; the wiki rates it the weakest |
| **Luxtructosaurus** (AC) | 600 | 12 | 20 armour |
| **Echo of Tyros** (Iron's) | 1000 | 10 | 15 armour |
| Void Worm (Alex's Mobs) | 160 (pack config) | 5 | Segmented, End only |

**Cataclysm's main bosses are post-Ender-Dragon content.** Besides having more health than the Dragon or the Wither,
they have damage caps in `config/cataclysm-common.toml` (e.g. the Ender Guardian takes at most 22 per hit and 13
per second, the Netherite Monstrosity 25 and 20), so they can't be burst down with gear alone. Several attacks also
take a percentage of the player's max health, which armour doesn't reduce. They're built for full netherite and
learning their patterns. Their mini-bosses (110-225 health) fit the mid-game and guard the same structures, so
players can meet a Cataclysm structure early, clear its outer parts, and come back for the boss.

## Proposed order

Six acts: four before the Dragon by gear tier and place, then the Dragon, then a post-game act for Cataclysm and the
other giants. Inside an act the order is a suggestion; the quest book can let players pick (`after_any`) and require
all of them for the act's finale.

### Prologue: the quiet forest (wood, stone)
Getting Started, the first village, the Field Guide, skills, mailbox, first home. The cleric explains the forest
has gone quiet.

### Act I: the first wardens (iron)
Mowzie's bosses are part of the main story (Acts I and II), not a side branch: each is a story beat, unlocked in the
compass when the story reaches it, and each drops gear that carries the player to the next act.
1. **YUNG's dungeons, mineshafts, desert and jungle temples**; the first structures in the compass.
2. **Ferrous Wroughtnaut** (Wrought Chamber): 40 health but hits for 30, only hurt from behind; teaches
   dodge-and-punish. Drops the **Wrought Axe** and **Wrought Helm**.
3. **Iron's Spells start** (also the start of the magic questline, below): a Priest, the Pyromancer Tower.
4. **Pillager outposts and the first raid**, the Illusioner and Iceologer (Friends & Foes).
5. **Umvuthi** (Umvuthana Grove, savanna; 150 health, spells and followers): drops the **Sol Visage**.
- _Act finale:_ Umvuthi falls; craft a diamond and light the **Twilight Forest portal**.

### Act II: below and beyond (diamond)
1. **Twilight Forest, part 1**: Naga, Lich, Minoshroom.
2. **Frostmaw** (snowy biomes; 250 health): drops the **Ice Crystal**.
3. **Alex's Caves**: Cave Maps; Magnetic and Primordial Caves, the Abyssal Chasm, Forlorn Hollows (**Forsaken**),
   the Candy Cavity.
4. **Elder Guardian** (Better Ocean Monument): prismarine, water breathing.
5. **Cataclysm's outposts**: scout the Cursed Pyramid (Kobolediator, Wadjet: Ancient Metal) and the Frosted Prison
   (Aptrgangr: Black Steel); their main bosses wait for the post-game.
6. **The Sculptor** (Monastery: a climbing trial up a tall peak, then the fight; fits the Agility tree and
   ParCool): drops the **Geomancer** armour set and the **Sculptor Staff**.
- _Act finale:_ the Sculptor's peak is the last Overworld trial; from the top you see the way into the Nether.
  **First trip to the Nether.**

Mowzie's Cataclysm's eyes (Wrought, Sun, Frostmaw, Tongbi) are crafted from Eyes of Ender, so they only work after
the first Nether trip. Before that, the story points the player at each Mowzie structure through the compass lock
(below); afterwards the eyes are a second way to find more of them.

### Act III: the burning realm (Nether, diamond to netherite)
1. **Better Nether Fortress**: blaze rods, wither skeleton skulls.
2. Friends & Foes' **Wildfire** (Nether citadel). Iron's Nether Citadel belongs to the magic questline.
3. **Netherite gear**.
4. **Twilight Forest, part 2**: Hydra, Knight Phantoms, Ur-Ghast.
5. Branch: **the Dead King** (Iron's Catacombs), the magic questline's big milestone.
6. **The Wither**, then a beacon.
7. Optional: **Hullbreaker** (Abyssal Chasm), **Tremorzilla** (Toxic Caves).
- _Act finale:_ finish the Twilight Forest (part 3 below) or find the stronghold.

### Act IV: the end (full netherite)
1. **Twilight Forest, part 3**: Alpha Yeti, Snow Queen.
2. **Stronghold** (YUNG's Better Strongholds) and the **Ender Dragon** (Better End Island).
3. **End cities**: elytra and shulker shells; Moog's End structures, Nullscape.
4. Optional: the **Void Worm** (End only), the **Warden**.
- _Act finale:_ the Dragon is down, and the eyes are all craftable now. The real threat shows itself.

### Act V: the reckoning (post-game: Cataclysm and the giants)
Ordered by the owner's own testing (easiest first). This replaces the wiki-based order: the wiki's ratings agree on
Ignis being hardest and the Netherite Monstrosity weakest, but testing put Maledictus and the Leviathan above the
Ancient Remnant (Maledictus's lift-and-slam one-shot a player in full Protection IV netherite with golden-apple
hearts, made worse by server lag).

1. **Netherite Monstrosity** (Soul Black Smith, Monstrous Eye). Easiest: two Ignited Revenants beat it in testing.
2. **Ender Guardian** (Ruined Citadel in the End, Void Eye): Gauntlet of Guard.
3. **The Harbinger** (Ancient Factory, Mech Eye): Witherite. It mirrors the Wither from Act III.
4. **Scylla** (Acropolis, Storm Eye).
5. **Ancient Remnant** (Cursed Pyramid, Desert Eye): annoying but doable. Ancient Metal, Sandstorm in a Bottle
   (with the Gauntlet of Guard: Gauntlet of Maelstrom).
6. **The Leviathan** (Sunken City, Abyss Eye, Abyssal Sacrifice).
7. **Maledictus** (Frosted Prison, Cursed Eye): Cursium. Warn players about the lift-and-slam; consider lowering
   its damage in `config/cataclysm-common.toml` if it stays a one-shot on the server.
8. **Ignis** (Burning Arena, Flame Eye): Ignitium. Hardest, no question.

**Ignis is the final boss of the main story**: the hardest fight in Cataclysm, last in the order above, and the
end of the plot. Side branches from the main quest (not required for the finale): **Luxtructosaurus** (Alex's
Caves volcano, Ominous Catalyst; 600 health, 20 armour), the Void Worm, the Warden. **Echo of Tyros** is the final
boss of the magic questline instead (below).

## Quest structure

### Principles (from the owner)

- **Nothing is locked behind quests.** Players can find bosses with eyes, compasses or by exploring, and kill them
  without being on the quest. Quests are a **pathway** to the content, with **helpful bonuses** along the way
  (gear, unique items, artifacts, skill XP), not a gate.
- **Quest progress is required for later quests.** Each questline is a chain; you can't skip ahead in it.
- **Doing something outside its quest doesn't complete the quest.** Beating Echo of Tyros without the magic
  questline is fine, but the questline's Tyros quest still isn't done. FTB Quests already works this way for
  kills: a kill task only counts while its quest is open (checked in its code). So boss quests ask for the
  **kill** (and story steps around it), never "have the boss's drop" or "have the boss's advancement", which
  would tick at once (see "What counts, and when" in `tools/quests/README.md`).
- **Variety, not just "go kill this boss".** Each boss beat is a few steps of different kinds (below).
- **Realms branch off.** Each dimension (and the Alex's Caves underworld) has its own questline, linked from the
  point in the main story where it fits.
- **The world hands out quests too.** Finding an item, a dungeon or a biome can start a standalone quest about it.
- **Artifacts become quest rewards** (note below).

### Main story and realm questlines

- **Main story** (group "The Story"): the Overworld spine, one chapter per act, Prologue to the Act V finale (Ignis).
  Its quests must be done in order.
- **Realm questlines** (group "Realms"), each its own chapter (or a few), starting from a main-story quest and
  linked back into it with a **quest link** so the main chapter shows where each realm falls:

| Realm | Opens from | Covers | Feeds back into |
|---|---|---|---|
| **Twilight Forest** | Act I finale (the portal) | Three parts: Naga/Lich/Minoshroom (Act II), Hydra/Knight Phantoms/Ur-Ghast (Act III), Yeti/Snow Queen (Act IV) | Twilight gear (Ironwood, Steeleaf, Knightmetal, Fiery) |
| **The Underworld** (Alex's Caves) | Act II | Cave Maps, each cave biome and its challenge, Forsaken, Hullbreaker, Tremorzilla, and the **Luxtructosaurus** finale | Cave tech and gear |
| **The Nether** | Act II finale (first trip) | Fortresses, bastions, Wildfire, netherite, the Wither; later the Nether Cataclysm bosses (Netherite Monstrosity, Ignis) as Act V links | Blaze powder (eyes), netherite, a beacon |
| **The End** | Act IV (the stronghold) | The Dragon, End cities, elytra, Moog's End structures, Nullscape, Void Worm; later the Ender Guardian | Shulker shells, elytra |

  The main story's acts then read as: Overworld beats, plus "the Twilight Forest is calling: go when ready (Part
  1)". Each realm chapter's quests can require main-story quests so realm progress can't run ahead of the story
  where it matters.
- **Side questlines** (other groups): the magic questline (Iron's Spells to Echo of Tyros), skill paths, villages
  and drops, mod showcases.

### Quest goal variety

A boss beat is a short chain, not one kill. The framework already supports all of these:

| Goal | Task type | Example |
|---|---|---|
| Learn about it from someone | `talk`, `giver` | A cleric tells you about the Frostmaw; a cartographer reads your cave tablet |
| Find it | `structure`, `biome`, `dimension`, `discover` | Reach the Umvuthana Grove; enter the Twilight Forest |
| Prepare | `item` (crafted or gathered) | Craft the Frostmaw Eye; gather the Abyssal Sacrifice's blocks; brew fire resistance |
| Scout | `observe` | Look at the Wroughtnaut's chamber door before going in |
| Clear the way | `kill` mini-bosses or mobs | Kobolediators and Wadjets before the Ancient Remnant |
| The fight | `kill` | Defeat the boss (counts only while the quest is open) |
| Aftermath | `item` (consume), `talk` | Bring the Ice Crystal back to the cleric; deliver a trophy |
| Travel and skill | `stat`, `levels` | Walk 10 km; fly 5 km with elytra; catch 100 fish |
| Build or decide | `checkmark` | Build a shrine; choose a path |

Rule of thumb: every boss beat has at least three steps of different kinds, and story text in each.

### Quest types

Every questline mixes these. Most are built; two need new mechanics (marked).

| Type | What the player does | How it's built |
|---|---|---|
| **Fetch** | Gather and hand over items | `item` with `"consume": true` |
| **Delivery** | Bring something to a particular person | `item` + `talk` |
| **Kill** | Defeat a number of a mob | `kill` (counts only while the quest is open) |
| **Boss** | A short chain: learn of it, find it, prepare, clear the way, fight, aftermath | Several steps, the fight is a `kill` |
| **Unique drop** | Hunt particular mobs until one drops a unique quest item | `drop` task: the item only drops while the quest is open (built) |
| **Discovery** | Stumble on something in the world, which starts a quest | `discover` (built) |
| **Exploration** | Reach a structure, biome or dimension | `structure`, `biome`, `dimension` |
| **Crafting** | Make a particular item | `item` with `"crafted": true` |
| **Story / talk** | Speak to characters, make choices | `giver`, `talk`, `checkmark` |
| **Milestone** | Travel, catch, mine a lot | `stat` (lifetime totals) |
| **Encounter** *(new mechanic)* | A quest step brings a character or creature into the world near the player: a trapped miner to rescue, a legendary beast to hunt, a rival to beat | KubeJS: when a step opens (talk/accept/discover), summon a named mob or NPC nearby (or in a matching biome/depth); its kill or rescue completes the step |
| **Timed challenge** *(new mechanic)* | Do something within a time limit: a fishing round, a courier run, holding a position | KubeJS: a step starts a timer and counts the action; succeeding within the limit adds the step's stage, failing lets the player retry |

### Skill paths: each with its own story and feel

Each skill path is its own short story with a mentor or rival and a setting, not a checklist. The owner's ideas are
the first three; the rest are proposals to approve or replace.

| Skill | Story and feel | Leans on |
|---|---|---|
| **Range** | **The hunt**: a hunting lodge; tracking game across biomes, then legendary trophy beasts | Unique drops, encounters |
| **Fishing** | **Fishing competitions**: a rival angler and a season of contests across waters, ending in a championship | Timed challenges, milestones |
| **Mining** | **Mining rescues**: a collapsed mine and trapped miners, each rescue deeper than the last | Encounters, exploration |
| Foraging | A herbalist's almanac: cataloguing wild plants and restoring a dying grove | Fetch, discovery |
| Farming | The harvest festival: prize crops and feeding a village through a hard season | Fetch, crafting |
| Cooking | A tavern kitchen: cooking for travellers, a food critic, feasts for village events (Dungeons & Taverns' taverns) | Delivery, crafting |
| Crafting | A guild apprenticeship: commissions from a master, rebuilding the village workshop and a bridge | Crafting, delivery |
| Attack | The monster hunter: the bounty board (Bountiful) and an arena ladder | Kill, unique drops, boss |
| Defense | The village guard: a guard captain (Guard Villagers), raids, fortifying a village | Kill, timed challenges |
| Agility | The courier: deliveries against the clock, rooftop routes (ParCool), wings | Timed challenges, milestones |
| Magic | The magic questline (Iron's Spells) to Echo of Tyros | Story, boss |
| Taming | The sanctuary: rescuing and raising animals, Domestication Innovation, unicorns | Encounters, delivery |

The sample Fishing path written earlier is a plain checklist; it gets rewritten as the competition story.

### Who gives quests (decided: all three kinds)

| Kind | Who | Used for | How it works |
|---|---|---|---|
| **Organisation representatives** | Villagers of a profession, standing in for an organisation in every village | Side quests and the skill paths' everyday quests | Each organisation has a **pool** of quests. A villager offers one picked from the pool by that villager's own identity, so different villages hand out different work. A player's progress in an organisation's storyline carries over: any representative, in any village, offers the next step |
| **Named characters at spawn** | Specific named NPCs placed in the spawn town, one shared copy each | Main-story beats and each organisation's leader (its storyline's key moments) | Matched by type and name. An op places them with a command; they don't despawn, wander off or take damage |
| **Characters who come to you** | A character appears near the player when a quest step opens, and stays for a while | Moments that happen out in the world: a messenger, someone lost or in trouble, a rival | The encounter mechanic: the step summons the named character nearby; talking to them (or helping them) completes the step |

Progress is still per player and in order whichever kind of giver offers it.

**Organisations (proposal)**: one per skill path, represented by the profession that fits it.

| Organisation (working names) | Skill path | Representatives |
|---|---|---|
| Hunters' lodge | Range | Fletchers |
| Anglers' society | Fishing | Fishermen |
| Miners' guild | Mining | Armourers / toolsmiths |
| Herbalists | Foraging | Clerics |
| Growers' co-operative | Farming | Farmers |
| Tavern keepers | Cooking | Butchers |
| Crafters' guild | Crafting | Masons |
| Bounty office | Attack | Weaponsmiths |
| Village watch | Defense | Guards (Guard Villagers) |
| Couriers | Agility | Cartographers |
| The arcane order | Magic | Librarians and Iron's Priests |
| Sanctuary keepers | Taming | Shepherds / leatherworkers |

Wandering traders can carry rare, one-off offers.

**To build** (framework, no content):
1. **Quest pools**: a giver can be a pool; the script picks one quest per villager (stable for that villager) from those the player can take now.
2. **Named NPCs**: a `/questnpc` command for ops to place a named character (villager or other mob, with profession and name) that stays put and can't be hurt; givers and talk steps match it by name.
3. **Encounters**: a quest step that summons its character near the player when it opens, and removes it when done or after a while.
4. **Timed challenges** (from the quest types above).

### Quests found in the world (discovery quests)

Standalone quests with `"discover"`: they're hidden until the player happens to do the trigger, then appear with a
toast. No NPC or script needed, and they work with or without the main story.

- **Finding an item:** a Cave Tablet → "take it to a cartographer"; a music disc → "find a jukebox and play it";
  an echo shard → "the ancient city's secret".
- **Entering a dungeon or structure:** a YUNG's skeleton dungeon → "clear it out"; a When Dungeons Arise
  stronghold → its own short quest; a Cataclysm stronghold → "you're not ready yet... (come back after Act IV)".
- **Entering a biome:** cherry grove, mushroom fields, each Alex's Caves biome, the Twilight biomes.
- **Milestones:** walking 1 km starts "The Long Walk" (10 km).

The sample chapter `tools/quests/src/chapters/out_in_the_world.json` has one of each.

### Artifacts as quest rewards

**Note: make artifacts rare in loot and give pretty much all of them as quest rewards.** The Artifacts mod's
config has the knobs: `artifactRarity` (above 1 makes artifacts rarer in chests; 10000 removes them from chest
loot entirely), `archaeologyChance` (suspicious sand/gravel) and the campsite settings (campsites hold artifacts in
chests and mimics; main already retrogens campsites into old chunks). Also check whether the Loot Integrations
add-ons add artifacts to structure loot. Then spread nearly all 40+ artifacts over the skill paths, realm
questlines and discovery quests (the skill-path table below already places most of them).

## The magic questline (Iron's Spells), ending with Echo of Tyros

The Magic skill path and Iron's Spells' content are one questline, running alongside the main story and branching
off it at each act. Its final boss is **Echo of Tyros, First Flamebearer** (1000 health, 15 armour), the strongest
fight in the pack, so it sits at the very end for the players who follow magic all the way.

| Main story | Magic questline |
|---|---|
| Act I | A village Priest; the Pyromancer Tower; first spellbook, scrolls and inks; the Apothecarist's mangrove hut |
| Act II | The Cryomancer's mountain tower; the Ice Spider den; the Evoker Fort's Archevoker; the arcane anvil and higher inks |
| Act III | The Catacombs and their Necromancers; **the Dead King** (500 health) |
| Act III-IV | The Nether Citadel and Ancient Battleground (**Ancient Knight**: cinder essence); pyrium |
| After Act V | Craft the **Tyros Statue** (pyrium ingot) and face **Echo of Tyros** |

Rewards along it: Magic skill XP, Iron's gear and scrolls, the Antidote Vessel, Scarf of Invisibility and Shock
Pendant (Artifacts), and a unique named staff or spellbook at the end.

## Skill paths: questlines tied to the skill trees

One chapter per Pufferfish skill tree in a "Skill Paths" group. Each path has 6-8 quests built around that skill's
activities; every quest gives skill XP in its tree, mid-path quests give an **Artifacts** item that suits the skill,
and the capstone gives a **unique named, enchanted item**. The Fishing path is written as the sample
(`tools/quests/src/chapters/skill_fishing.json`).

| Skill | Path activities | Artifacts rewards | Capstone unique item (example) |
|---|---|---|---|
| Mining | Ores by depth, deepslate, mineshafts, ancient debris | Digging Claws, Night Vision Goggles, Lucky Scarf, Pickaxe Heater | Fortune/Efficiency pickaxe |
| Foraging | Logs of many kinds, wild plants, saplings, cave plants | Universal Attractor, Rooted Boots | Unbreakable axe |
| Farming | Crops, Farmer's Delight / Farm & Charm crops, animals bred | Rooted Boots, Villager Hat | Named hoe |
| Fishing (sample) | Cod, salmon, tropical fish, pufferfish, treasure, nautilus, neptunium | Snorkel, Angler's Hat, Flippers | Tidecaller (Neptunium rod, Luck of the Sea III, Lure III, unbreakable) |
| Cooking | Meals from each cooking mod, feasts, drinks | Eternal Steak, Everlasting Beef, Novelty Drinking Hat, Onion Ring | Named cleaver or knife |
| Crafting | Workstations, tools, storage, Obscura's storage network | Villager Hat, Universal Attractor, Pocket Piston | Named tool set |
| Attack | Hostile mobs, mini-bosses, Spartan weapons | Power Glove, Feral Claws, Fire Gauntlet, Vampiric Glove | Named Spartan weapon (Sharpness, Looting) |
| Range | Bow and crossbow kills, long shots, thrown weapons | Superstitious Hat, Golden Hook | Named bow (Power, Infinity) |
| Defense | Shields blocked, armour sets, surviving bosses | Crystal Heart, Cross Necklace, Steadfast Spikes, Thorn/Flame/Shock Pendant, Chorus Totem | Named shield or chestplate (Protection, Unbreaking) |
| Agility | Distance travelled, ParCool moves, climbing, wings | Running Shoes, Bunny Hoppers, Cloud in a Bottle, Helium Flamingo, Panic Necklace, Snowshoes, Aqua-Dashers | Named boots (Feather Falling, Depth Strider) |
| Magic | The magic questline above (Iron's Spells), ending with Echo of Tyros | Antidote Vessel, Scarf of Invisibility, Shock Pendant | Named spellbook or staff |
| Taming | Pets, mounts, unicorns, Domestication Innovation | Cowboy Hat, Kitty Slippers | Named saddle or lead (cosmetic) |

Artifacts also spawn in loot, so quest artifacts should be the ones that suit the path rather than the rarest.

## Locking the compasses behind quests (decided, not built yet)

Explorer's Compass and Nature's Compass would otherwise find any structure or biome from day one, skipping the
story's discovery. **Decision: the real lock only**: players craft the compass normally, but what it can find
grows with their quest progress. No recipe lock, and no extra check against modified clients (not a concern on this
server). Not to be built until asked.

This fits "nothing is locked behind quests": the lock only limits what the **compass** shows. Eyes (Cataclysm,
Mowzie's Cataclysm), maps, and plain exploring still find everything, so a player can always reach a boss early;
the compass just becomes the quest pathway's guide.

- **How:** both compasses build the list of searchable structures/biomes **on the server, per player, when the
  compass is used** (`ExplorersCompassItem.use` calls `StructureUtils.getAllowedStructureKeys` and sends a
  `SyncPacket` to that player; Nature's Compass does the same with biomes). One mixin per compass filters that list
  by the player's quest stages, so locked entries don't appear in the compass at all.
- **Where the locks live:** next to the quests, e.g. a quest with `"unlocks": {"structures": ["mowziesmobs:wrought_chamber"]}`.
  The generator gives that quest an invisible stage reward and writes the lock list for the mod to read; anything
  not mentioned stays unlocked.
- **Suggested locks:** Mowzie's structures as their story beat starts (Wrought Chamber, Umvuthana Grove, Frostmaw,
  Monastery); Alex's Caves biomes with the caves branch; Iron's Catacombs and Citadel with the magic questline;
  End structures after the Dragon; the Cataclysm strongholds one by one through Act V.
- **Code:** a mixin into each compass, in its own small mod (e.g. "FOTF Quests", like FOTF Retrogen), which can
  later hold other quest hooks too.

## Story hooks (placeholder, to shape together)

- **Theme:** the forest spirits have gone quiet because something is draining the world's wardens. Each act's
  bosses are "wardens" turned or woken by it, and the Twilight Forest is the spirits' own realm, visited in three
  parts as the story deepens.
- **Prologue / Act I:** the village cleric and the first signs. The Wroughtnaut and Umvuthi guard old places.
- **Act II:** the corruption is below: the caves, and the sealed Cataclysm strongholds you can't yet enter.
- **Act III:** the Nether, the Dead King and the Wither: the world's wardens are being turned.
- **Act IV:** the Dragon falls, and with the Void's guard gone, the eight sealed strongholds wake.
- **Act V:** the reckoning: break the eight; the last of them, Ignis, is the source of it all.
- **Magic questline:** the First Flamebearer, Tyros, is the magic path's own ending.
- Recurring NPCs (villager givers and name-tagged NPCs) carry the story between acts; side quests come from
  villagers, mob drops and found items, as the quest framework already supports.

**Wiki ratings** (L_Ender's Cataclysm wiki, per-boss pages; the Bosses index page couldn't be read from the cloud
session): Hard: Netherite Monstrosity, Ender Guardian, Ancient Remnant, The Harbinger. Very Hard: Maledictus,
Scylla. Insane: Ignis. The Leviathan: not found. Some pages (Scylla, Maledictus, Harbinger) may be out of date.

## Open questions

- Should acts lock the next act's quests, or just suggest an order? (Bosses themselves can't be locked; their
  structures can be hidden from the compass.)
- Where do the optional fights go: Warden, Void Worm, Hullbreaker, Tremorzilla?
- Should Maledictus's damage be lowered for the server (lag made its slam a one-shot in testing)?
- Confirm in game: how Echo of Tyros is summoned, and the Alex's Caves bosses' summon steps in this version.
