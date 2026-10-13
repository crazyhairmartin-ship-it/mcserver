# Boss and objective progression (for the story line)

Status: proposal for discussion, 2026-10-13. Built from the pack's current mod list on `main` (merged into
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

## Proposed order

Five acts, each matching a gear tier and a new place, so the story is also the progression guide. Inside an act
the order is a suggestion; the quest book can let players pick (`after_any`) and then require all of them for the
act's finale.

### Prologue: the quiet forest (wood, stone)
Getting Started, the first village, the Field Guide, skills, mailbox, first home. The cleric explains the forest
has gone quiet.

### Act I: the first wardens (iron)
1. **Ferrous Wroughtnaut** (Wrought Chamber): small health, armoured from the front; teaches dodge-and-punish.
2. **YUNG's dungeons, mineshafts, desert and jungle temples**: loot and the first Explorer's Compass.
3. **Iron's Spells start**: a Priest in a village, the Pyromancer Tower, first spellbook and scrolls.
4. **Umvuthi** (Umvuthana Grove, savanna).
5. **Pillager outpost / first raid**, Illusioner and Iceologer (Friends & Foes).
- _Act finale:_ craft a diamond tool and light the **Twilight Forest portal**.

### Act II: below and beyond (diamond)
1. **Twilight Forest, part 1**: Naga, Lich, Minoshroom.
2. **Alex's Caves**: get Cave Maps; Magnetic Caves, Primordial Caves (summon **Luxtructosaurus** with the Ominous
   Catalyst), Abyssal Chasm (**Hullbreaker**), Forlorn Hollows (**Forsaken**), Candy Cavity. Toxic Caves and
   Tremorzilla can wait for Act III.
3. **Frostmaw** (snowy biomes) and the **Sculptor** (Monastery climb; a good fit for the Agility tree and ParCool).
4. **Elder Guardian** (Better Ocean Monument): prismarine for later, water breathing.
5. **Ancient Remnant** (Cursed Pyramid), after its mini-bosses Kobolediator and Wadjet: Ancient Metal.
6. **The Dead King** (Iron's Catacombs, after its Necromancers): the big magic milestone.
7. **Evoker Fort** (Archevoker) and When Dungeons Arise's illager strongholds.
- _Act finale:_ the **first trip to the Nether** (blaze powder makes the eyes possible).

### Act III: the burning realm (Nether, diamond to netherite)
1. **Better Nether Fortress**: blaze rods, wither skeleton skulls.
2. **Iron's Nether Citadel**: the **Ancient Knight**; Friends & Foes' **Wildfire** in its own Nether citadel.
3. **Netherite Monstrosity** (Soul Black Smith, Monstrous Eye).
4. **Netherite gear**, then **Echo of Tyros** (Iron's, pyrium).
5. **Ignis** (Burning Arena, Flame Eye): Ignitium.
6. **Twilight Forest, part 2**: Hydra, Knight Phantoms, Ur-Ghast (fire themes fit this act).
7. **The Wither** (vanilla), then **The Harbinger** (Ancient Factory, Mech Eye): the machine that copies the Wither;
   Witherite.
8. **Maledictus** (Frosted Prison, Cursed Eye) after Aptrgangr: Cursium. Toxic Caves and **Tremorzilla** fit here.
- _Act finale:_ a beacon; the corruption's trail leads to the sea.

### Act IV: the deep and the storm (netherite)
1. **Conduit and deep-sea gear**; Moog's ocean structures.
2. **The Leviathan** (Sunken City, Abyss Eye, Abyssal Sacrifice), after the Coral Golem.
3. **Scylla** (Acropolis, Storm Eye): the hardest Overworld fight.
4. **Twilight Forest, part 3**: Alpha Yeti, Snow Queen (the Twilight Forest finished).
5. Optional: **the Warden** (ancient city).
- _Act finale:_ find the stronghold (YUNG's Better Strongholds) and open the End portal.

### Act V: the end of all things (the End)
1. **The Ender Dragon** (Better End Island).
2. **End cities**: shulker shells (Void Eye), elytra; Moog's End structures, Nullscape.
3. **Ender Guardian** (Ruined Citadel, after the Ender Golem).
4. Optional super-boss: **the Void Worm** (Alex's Mobs).
- _Finale:_ a capstone quest that needs the act finales (and, for completionists, every boss trophy or music disc).
  The forest wakes up.

## Story hooks (placeholder, to shape together)

- **Theme:** the forest spirits have gone quiet because something is draining the world's wardens. Each act's
  bosses are "wardens" turned or woken by it, and the Twilight Forest is the spirits' own realm, visited in three
  parts as the story deepens.
- **Prologue / Act I:** the village cleric and the first signs. The Wroughtnaut and Umvuthi guard old places.
- **Act II:** the corruption is below: the caves, the catacombs, the Dead King.
- **Act III:** it came from the Nether's forges (Monstrosity, Ignis, Tyros). The Harbinger is a machine built
  to copy the Wither.
- **Act IV:** it fled into the sea (Leviathan, Scylla).
- **Act V:** its source is the Void (Ender Guardian, the Void Worm).
- Recurring NPCs (villager givers and name-tagged NPCs) carry the story between acts; side quests come from
  villagers, mob drops and found items, as the quest framework already supports.

## Open questions

- Should acts lock the next act (quests only, since bosses can't be locked) or just suggest an order?
- Where do the optional/very hard fights go: Warden, Void Worm, Scylla?
- Is Mowzie's Sculptor better as an Act II climb or an Act III challenge?
- Confirm in game: how Echo of Tyros is summoned, and the Alex's Caves bosses' summon steps in this version.
