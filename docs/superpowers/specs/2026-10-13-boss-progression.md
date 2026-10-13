# Boss and objective progression (for the story line)

Status: proposal for discussion, 2026-10-13 (revised: Cataclysm's main bosses moved after the Ender Dragon and ordered by the owner's testing; Mowzie's bosses in the main story; Ignis the final boss and Echo of Tyros the magic questline's; compass real lock decided, not built). Built from the pack's current mod list on `main` (merged into
`claude/cloud-session-setup-epiuzy`), reading each mod's jar: boss tags, structures and where they generate, locator
recipes, and boss loot tables. Difficulty is relative (from the mods' designs and drops), not measured in game.

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

## Quest structure: a main quest with branches

Quests are the pack's progression, not an optional extra: the main story and its branches carry real rewards
(boss-tier gear, unique items, artifacts, skill XP), and the compass lock ties discovery to them.

- **Main quest** (group "The Story"): one chapter per act. Each act has a short spine of story quests that must be
  done in order, ending in the act's finale. The spine only asks for what the plot needs.
- **Branches**: optional content hangs off the spine. A spine quest unlocks a branch questline in its own chapter
  (side content, a mod showcase or a big optional boss like the Luxtructosaurus). The spine chapter shows the
  branch with a **quest link** (`"links"` in the chapter source): it appears in the main chapter, and clicking it
  opens the branch. Branches can loop back with a reward that helps the spine (e.g. the Luxtructosaurus branch
  gives gear that makes Act V easier).
- **Planned branches** (first pass):

| Branches off | Branch | Content |
|---|---|---|
| Act I spine | The magic questline | Iron's Spells from the first Priest to Echo of Tyros (below) |
| Act II spine | Alex's Caves | Cave Maps, each cave biome, Forsaken, Hullbreaker, Tremorzilla, **Luxtructosaurus** |
| Act II spine | Twilight Forest | Three parts, continued in Acts III and IV |
| Act II spine | Cataclysm scouting | Mini-bosses, eyes, the eight sealed strongholds |
| Act IV spine | The End | End cities, elytra, Moog's End structures, Void Worm |
| Act V spine | The eight | One branch quest per Cataclysm boss, in the order above |
| Any time | Skill paths | One questline per skill tree (below) |
| Any time | Villages, drops, exploration | Villager and mob givers, drop quests, structures and biomes to find |

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
