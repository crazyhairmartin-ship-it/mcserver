# Boss and objective progression (for the story line)

Status: proposal for discussion, 2026-10-13 (revised: Cataclysm's main bosses moved after the Ender Dragon and ordered by the Cataclysm wiki's difficulty ratings; base health from each mod's code). Built from the pack's current mod list on `main` (merged into
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
1. **Ferrous Wroughtnaut** (Wrought Chamber): 40 health but hits for 30; teaches dodge-and-punish.
2. **YUNG's dungeons, mineshafts, desert and jungle temples**; the first Explorer's Compass.
3. **Iron's Spells start**: a Priest in a village, the Pyromancer Tower, first spellbook and scrolls.
4. **Umvuthi** (Umvuthana Grove, savanna).
5. **The Sculptor** (Monastery climb; fits the Agility tree and ParCool).
6. **Pillager outposts and the first raid**, the Illusioner and Iceologer (Friends & Foes).
- _Act finale:_ craft a diamond and light the **Twilight Forest portal**.

### Act II: below and beyond (diamond)
1. **Twilight Forest, part 1**: Naga, Lich, Minoshroom.
2. **Alex's Caves**: Cave Maps; Magnetic and Primordial Caves, the Abyssal Chasm, Forlorn Hollows (**Forsaken**),
   the Candy Cavity.
3. **Frostmaw** (snowy biomes).
4. **Elder Guardian** (Better Ocean Monument): prismarine, water breathing.
5. **Cataclysm's outposts**: scout the Cursed Pyramid (Kobolediator, Wadjet: Ancient Metal) and the Frosted Prison
   (Aptrgangr: Black Steel); their main bosses wait for the post-game.
6. **Evoker Fort** (Archevoker) and When Dungeons Arise's illager strongholds.
- _Act finale:_ the **first trip to the Nether**.

### Act III: the burning realm (Nether, diamond to netherite)
1. **Better Nether Fortress**: blaze rods, wither skeleton skulls.
2. **Iron's Nether Citadel** (Ancient Knight) and Friends & Foes' **Wildfire**.
3. **Netherite gear**.
4. **Twilight Forest, part 2**: Hydra, Knight Phantoms, Ur-Ghast.
5. **The Dead King** (Iron's Catacombs): the big magic milestone.
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
Ordered by the Cataclysm wiki's own difficulty ratings (Hard, Very Hard, Insane), not by health: the wiki calls the
600-health Netherite Monstrosity the weakest boss and Ignis the hardest. Each tier's drops help with the next.

_Hard_
1. **Netherite Monstrosity** (Soul Black Smith, Monstrous Eye): the wiki's weakest boss, a good first Cataclysm fight.
2. **Ender Guardian** (Ruined Citadel in the End, Void Eye): Gauntlet of Guard.
3. **Ancient Remnant** (Cursed Pyramid, Desert Eye): Ancient Metal, Sandstorm in a Bottle (with the Gauntlet of
   Guard: Gauntlet of Maelstrom).
4. **The Harbinger** (Ancient Factory, Mech Eye): Witherite. It mirrors the Wither from Act III.

_Very Hard_
5. **The Leviathan** (Sunken City, Abyss Eye, Abyssal Sacrifice). No wiki rating was found; placed here because
   it needs the Abyssal Sacrifice and an underwater fight.
6. **Maledictus** (Frosted Prison, Cursed Eye): Cursium.
7. **Scylla** (Acropolis, Storm Eye).

_Insane_
8. **Ignis** (Burning Arena, Flame Eye): Ignitium. The wiki's hardest Cataclysm boss.

Then the other giants:
9. **Luxtructosaurus** (Alex's Caves volcano, Ominous Catalyst): 600 health, 20 armour.
- _Finale:_ **Echo of Tyros, First Flamebearer** (Iron's, 1000 health, 15 armour): the strongest thing in the pack
  and a natural final boss. A capstone quest needs it plus the act finales; completionists collect every trophy
  or music disc.

The Hard tier could also come just before the Dragon (the Netherite Monstrosity and the Harbinger fit Act III's
Nether and Wither themes) for groups that want an earlier challenge. The Ender Guardian can't: it lives in the End.

## Story hooks (placeholder, to shape together)

- **Theme:** the forest spirits have gone quiet because something is draining the world's wardens. Each act's
  bosses are "wardens" turned or woken by it, and the Twilight Forest is the spirits' own realm, visited in three
  parts as the story deepens.
- **Prologue / Act I:** the village cleric and the first signs. The Wroughtnaut and Umvuthi guard old places.
- **Act II:** the corruption is below: the caves, and the sealed Cataclysm strongholds you can't yet enter.
- **Act III:** the Nether, the Dead King and the Wither: the world's wardens are being turned.
- **Act IV:** the Dragon falls, and with the Void's guard gone, the eight sealed strongholds wake.
- **Act V:** the reckoning: break the eight, then face the First Flamebearer, the source of it all.
- Recurring NPCs (villager givers and name-tagged NPCs) carry the story between acts; side quests come from
  villagers, mob drops and found items, as the quest framework already supports.

**Wiki ratings** (L_Ender's Cataclysm wiki, per-boss pages; the Bosses index page couldn't be read from the cloud
session): Hard: Netherite Monstrosity, Ender Guardian, Ancient Remnant, The Harbinger. Very Hard: Maledictus,
Scylla. Insane: Ignis. The Leviathan: not found. Some pages (Scylla, Maledictus, Harbinger) may be out of date.

## Open questions

- Should acts lock the next act (quests only, since bosses can't be locked) or just suggest an order?
- Where do the optional fights go: Warden, Void Worm, Hullbreaker, Tremorzilla?
- Is Echo of Tyros the final boss, or should the story end on a Cataclysm boss (e.g. the Netherite Monstrosity)?
- Confirm in game: how Echo of Tyros is summoned, and the Alex's Caves bosses' summon steps in this version.
