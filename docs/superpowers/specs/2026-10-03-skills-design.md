# FOTF Skills: design

Status: draft for review (2026-10-03)

## What we're building

A learn-by-doing skills system for Friends of the Forest. You level a skill by doing it, and its levels give
points for that skill's talent tree. Spending points in lower tiers opens higher tiers, WoW style.

### What Dylan asked for

- Levels that make you better at the thing that trains them.
- The big perk: as you level, a growing chance to **not use up resources** or to **get more out**.
- Cover the modded systems: magic (Ars Nouveau + Iron's Spells, one shared tree) and taming.
- Talent trees with tiers: enough points spent in earlier tiers opens the next tier; some nodes need specific
  earlier nodes; some tiers are "pick one", others let you take everything.
- Lots of levels overall, but the bottom of a tree reachable with a medium amount of play.
- No hard locks. High-end actions (rare tames) just succeed less often at low levels.
- Combat XP from landed hits, not kills. Defense from taking or blocking hits.
- Taming improves taming *and* makes pets strong, so a player can fight through their pets (Fionah).
- Unique and conditional perks (pet scavenging, weapon-type damage, homing arrows, revive pets...).
- Preview trees first (nodes that do nothing) to try in game before any perk code is written.

### Assumptions (from the design chat)

- Bonuses are opt-in power only; nothing makes the world harder (project rule: combat stays opt-in).
- Progress is per player, saved on the server, everyone starts at level 1.
- XP is personal; no party sharing (landed hits already split fairly in group fights).
- Shared mana between Ars Nouveau and Iron's Spells is a **separate project after this one** (feasibility
  test first). The Magic tree's mana perks apply to whichever pool(s) exist at the time.

## How it fits together

1. **Pufferfish's Skills** (Modrinth `skills`, Forge 1.20.1, v0.19.x; server + client). Provides the skill
   menu, per-tree levels and points, unlock rules (`required_spent_points` for tiers, `required_skills` for
   prerequisites, exclusive nodes for choices, per-node `cost`), saving, level-up popups, built-in XP sources
   (mine/break block, kill, deal/take damage, heal, craft, smelt, enchant, fish, eat, any vanilla stat),
   per-mob/per-chunk anti-farming, and rewards (attributes, commands, tags, `dummy`). Trees are config files
   in the pack repo (`config/puffish_skills/` or a datapack under `kubejs/data/`).
2. **FOTF Skills add-on** (new, `extras/fotfskills/`, built like fotfmail: javac in Docker against the SRG
   jar; server + client). Registers custom XP sources and custom reward (perk) types through Pufferfish's API
   (`ExperienceSourceFactory`, `RewardFactory`). Kept separate from fotfmail.
3. **Plain attributes** need no code: attack damage, armour, toughness, max health, movement speed, knockback
   resistance, and the magic mods' attributes (Iron's `max_mana`, `mana_regen`, `spell_power`,
   `cooldown_reduction`; Ars Nouveau's max mana / mana regen / spell damage).

Each perk reward stores its numbers in the tree config (e.g. `{"type":"fotfskills:save_ammo","chance":0.05}`),
so balancing is a config edit. Perks of the same type add up (three ranks of +5% = +15%), with a per-type cap.

## Pacing

- Every skill caps at **level 50**, 1 point per level. Early levels are quick, later ones slower.
- The capstone tier opens at **25 points spent**: a focused player reaches the bottom of a tree in a few
  weeks of doing that activity.
- Filling everything open in a tree costs about **50 points**; choice tiers mean you never get every node.
- Starting XP curve (tune during the preview): XP for next level = `30 + 12 × level^1.35`.

### Tier template (all trees)

| Tier | Opens at (points spent in this tree) | Kind |
|---|---|---|
| 1 | 0 | Open |
| 2 | 5 | Open |
| 3 | 10 | Choice (pick one branch) |
| 4 | 15 | Open |
| 5 | 25 | Open extras + capstone choice |

"R3" = a node with 3 ranks, built as a chain of linked nodes costing 1 point each. Nodes in open tiers drafted
as R3 get **5 ranks**, so a full tree costs 40–49 points (close to the level-50 cap); choice and capstone
nodes stay at 3. Per-rank amounts are rebalanced in the preview. Arrows ("needs X") are
`required_skills`. Branch nodes in a choice tier are exclusive with the other branch.

## XP sources

| Skill | XP from |
|---|---|
| Mining | Mining natural stone/ores/deepslate (rarer ores worth more) |
| Woodcutting | Chopping natural logs, incl. modded trees |
| Farming | Harvesting fully grown crops; breeding farm animals |
| Fishing | Any catch (Aquaculture included) |
| Cooking | Finished meals: Farmer's Delight pots, Let's Do recipes, smoker/furnace food |
| Crafting | Crafting tools/armour/weapons/gear; smithing-table upgrades; smelting ingots |
| Attack | Landed melee hits, by damage dealt |
| Range | Landed projectile hits (thrown weapons too), more at long range |
| Defense | Hits taken from mobs (damage absorbed) and hits blocked with a shield (full credit) |
| Agility | ParCool moves (wall-run, climb, roll, vault, dodge), sprinting, gliding |
| Magic | Casting spells in either mod, by mana spent |
| Taming | Taming (rare animals worth more), feeding/healing pets, your pets landing hits |

Anti-farming: built-in per-mob and per-chunk limits; player-placed blocks give no Mining/Woodcutting XP;
falls, fire, drowning and self-inflicted damage give no Defense XP.

Custom sources needed (add-on): spell cast (Ars + Iron's), shield block (Forge `ShieldBlockEvent`), tame
(Forge `AnimalTameEvent` + mod-specific tames that skip it), pet feeding/healing, pet hits (owner credited),
ParCool actions, crop harvest (mature only), cooking-station outputs, smithing-table upgrades.

## Perk types

**Saving resources**: save ingredients (crafting/cooking/brewing inputs), save ammo, save mana (both mods),
save taming food, save durability.

**Extra output**: extra drops (ores, logs, crops, fish; not on top of Fortune for the same block), extra
servings (meals), twins (breeding).

**Activity boosts**: mining/chopping/harvesting speed, fishing bite speed, bow/crossbow draw speed,
projectile range (velocity), cooking-pot speed, ParCool + Paragliders stamina drain, less fall damage,
swim speed, taming success chance (level-scaled, with a minimum).

**Unique and conditional**:
- *Weapon-type damage*: bonus damage with two-handed (Spartan/Simply Swords greatswords, halberds, battle
  hammers, glaives...), thrown (javelins, tomahawks, throwing knives, tridents), daggers/rapiers, spears/pikes,
  axes, bows vs crossbows. Classified by item tags we ship (`fotfskills:two_handed`, `fotfskills:thrown`, ...).
- *Homing arrows*: chance an arrow curves to the nearest hostile mob.
- *Auto-smelt*: chance mined ore drops smelted.
- *Treasure sense*: better treasure odds, chance of a double catch.
- *Hearty meals*: cooked food gives more saturation and longer buffs.
- *Green thumb*: crops you plant may start at a later stage; crops near you grow faster.
- *Enchanted crafts*: chance a crafted tool/weapon/armour piece gets a random low-level enchantment.
- *Book saver*: an enchanted item that would break becomes an enchanted book with its enchantments.
- *Shield thorns*: chance a blocked hit reflects some damage.
- *Second wind*: once every few minutes, a killing blow leaves you on half a heart.
- *Quick casting*: shorter cooldowns; chance an Iron's scroll isn't used up.
- *Pet scavenging*: your pets sometimes drop found resources near you (tiered loot table).
- *Pack tactics*: pets deal more damage when attacking the same target as you.
- *Pet stats*: health/damage/armour/speed/regen for your tamed animals while you're within ~32 blocks.
- *Revive pets*: a pet that dies leaves a **Pet Memento** holding the whole pet (name, collar, armour, stats).
  With the perk, using the Memento revives it after a cost (time and/or an item); higher ranks make it cheaper.
  Covers tamed animals, Ars familiars and other owned companions.

## Tree drafts

Values are starting points for the preview; every number is a config value.

### Mining (pickaxe)
| Tier | Nodes |
|---|---|
| 1 | Stone Sense R3: +6% mining speed each · Steady Pick R3: 5% save durability each · Deep Lungs R2: +1 armour while below Y 40 each |
| 2 | Prospector R3: 4% extra ore drops each · Night Eyes: night vision underground after mining 20 blocks in a row · Hard Hat R2: −20% damage from falling blocks and cave mobs' first hit each |
| 3 choice | **Smelter**: 15% auto-smelt, then R2 +10% · **Gem Hunter**: 6% extra drops on gems (diamond, emerald, lapis, amethyst) R3 |
| 4 | Vein Tracker R3: Ultimine costs less hunger · Prospector II R3 (needs Prospector 3): +4% extra ore drops · Bedrock Grip R3: +8% speed on deepslate · Ore Nose: chance to drop raw nuggets from plain stone |
| 5 | Steady Pick II R3 · Tunnel Rat R2: +10% speed in caves · **Capstone choice**: *Motherlode* (2% chance an ore drops triple) or *Forge Heart* (auto-smelt also gives bonus XP orbs and 10% double ingots) |

### Woodcutting (axe)
| Tier | Nodes |
|---|---|
| 1 | Lumberjack R3: +8% chopping speed · Sapling Sense R3: +10% sapling/apple drops · Axe Care R2: 6% save durability |
| 2 | Timber R3: 5% extra logs · Bark Stripper: stripping gives bark/sticks · Forester R2: saplings you plant grow 15% faster |
| 3 choice | **Feller**: Ultimine on trees costs no hunger + R2 speed · **Woodworker**: 10% save planks/logs when crafting wood items R3 |
| 4 | Timber II R3 · Heartwood: 3% chance of a rare modded log/sap drop (BoP/RU woods) · Axe Mastery R3: +1 attack damage with axes · Leaf Cutter R2: leaves drop extra sticks/seeds |
| 5 | Lumberjack II R3 · **Capstone choice**: *Whole Tree* (5% chance the whole tree drops at once) or *Ancient Grove* (planted saplings 25% chance to grow instantly) |

### Farming (hoe)
| Tier | Nodes |
|---|---|
| 1 | Harvester R3: 5% extra crops · Seed Saver R3: 8% chance to get the seed back on replant · Hoe Care R2 |
| 2 | Green Thumb R3: crops you plant 6% chance to start a stage later · Rancher R2: breeding cooldown −15% · Fertile Soil R2: crops within 8 blocks of you grow 10% faster |
| 3 choice | **Gardener**: Green Thumb chance ×2 + R2 extra crops · **Herder**: Twins 6% R3 for farm animals |
| 4 | Harvester II R3 · Bountiful Bees: honey/comb bonus · Compost King: composter fills faster · Shepherd's Shears R2: extra wool/milk/eggs |
| 5 | Fertile Soil II R2 · Seed Saver II R2 · **Capstone choice**: *Harvest Moon* (5% chance a harvest drops double everything) or *Golden Herd* (twins also inherit better stats) |

### Fishing (fishing rod)
| Tier | Nodes |
|---|---|
| 1 | Patient Angler R3: −8% bite time · Lucky Line R3: +treasure odds · Rod Care R2 |
| 2 | Double Catch R3: 4% two fish at once · Bait Saver R2: 15% Aquaculture bait not used · Deep Diver R2: swim speed + longer breath |
| 3 choice | **Treasure Hunter**: treasure sense ×2 + R2 rarer loot table · **Fishmonger**: extra fish drops R3 + cooking fish gives extra |
| 4 | Patient Angler II R3 · Storm Fisher: faster bites in rain · Sea Legs R2: boat speed · Lure Master R3: Aquaculture lures stronger |
| 5 | Double Catch II R3 · **Capstone choice**: *Leviathan Bait* (rare chance of a unique trophy fish) or *Endless Supply* (25% rod durability never used, bait never used) |

### Cooking (Farmer's Delight cooking pot)
| Tier | Nodes |
|---|---|
| 1 | Thrifty Cook R3: 5% save an ingredient · Quick Hands R3: cooking pot / Let's Do stations 8% faster · Taste Tester R2: +1 hunger from your meals |
| 2 | Extra Serving R3: 5% one extra meal · Hearty Meals R3: +10% saturation · Brewer R2: Let's Do drinks (wine, beer, tea) 8% save ingredient |
| 3 choice | **Chef**: meal buffs last 50% longer + R2 extra servings · **Baker**: bakery/oven items double 8% R3 |
| 4 | Thrifty Cook II R3 · Spice Rack: meals give a small random bonus buff · Campfire Cook R2: campfire/smoker 20% faster · Picnic R2: eating near party members heals a little |
| 5 | Hearty Meals II R3 · **Capstone choice**: *Feast Maker* (feasts/pies give extra slices) or *Master Brewer* (aged drinks age 30% faster and save 15% ingredients) |

### Crafting (crafting table)
| Tier | Nodes |
|---|---|
| 1 | Frugal R3: 4% save an ingredient · Smith R3: crafted tools/armour +8% durability · Smelter R2: furnaces you use 10% faster |
| 2 | Enchanted Crafts R3: 3% random low enchant on gear crafts · Book Saver: breaking enchanted items become books · Repair Kit R2: anvil repairs cost less XP |
| 3 choice | **Weaponsmith**: crafted weapons 10% chance of +1 attack damage R3 · **Armourer**: crafted armour 10% chance of +1 toughness R3 |
| 4 | Frugal II R3 · Enchanted Crafts II R3 (needs I 3): better enchant levels · Salvager R2: grindstone returns materials · Quality Work R3: +durability II |
| 5 | Smelter II R2 · **Capstone choice**: *Masterwork* (2% crafts come out with two enchantments) or *Endless Workshop* (10% any craft uses no ingredients) |

### Attack (sword)
| Tier | Nodes |
|---|---|
| 1 | Sharpened R3: +0.5 attack damage · Blade Care R3: 5% save weapon durability · Footwork R2: +3% speed in combat |
| 2 | Crit Training R3: +10% crit damage · Lifeline R2: heal 0.5 heart on crits · Momentum R2: consecutive hits +5% damage (stacks to 3) |
| 3 choice | **Heavy Arms**: two-handed weapons +10% damage R3 · **Duelist**: daggers/rapiers/swords +8% attack speed R3 |
| 4 | Sharpened II R3 · Spearman R3: spears/pikes/lances +reach · Axe Master R2: axes disable shields longer · Executioner R2: +15% damage to mobs below 30% HP |
| 5 | Crit Training II R3 · **Capstone choice**: *Cleave* (two-handed hits splash 30% to nearby mobs) or *Flurry* (every 5th fast hit strikes twice) |

### Range (bow)
| Tier | Nodes |
|---|---|
| 1 | Steady Hands R3: +8% draw speed · Sharp Tips R3: +6% projectile damage · Quiver Care R2: 8% save ammo |
| 2 | Eagle Eye R3: +10% projectile velocity/range (needs Steady Hands 3) · Thrower R3: thrown weapons +8% damage · Long Shot R2: +XP and damage beyond 20 blocks |
| 3 choice | **Rapid Volley**: draw speed +15% R3 · **Heavy Draw**: damage +12% R3 |
| 4 | Quiver Care II R3 · Homing Arrows R3: 5% chance to home · Crossbowman R2: crossbows reload faster · Retriever R2: thrown weapons return chance |
| 5 | Eagle Eye II R2 · **Capstone choice**: *Fletcher's Luck* (30% save ammo and arrows sometimes drop back on hit) or *Seeker* (homing chance ×3 and headshot-style crits) |

### Defense (shield)
| Tier | Nodes |
|---|---|
| 1 | Toughened R3: +1 armour · Shield Wall R3: −15% knockback while blocking, shield durability lasts 10% longer · Armour Care R2: 5% save armour durability |
| 2 | Iron Skin R3: +0.5 armour toughness · Shield Thorns R2: 8% reflect 30% of blocked damage · Vitality R2: +2 max health |
| 3 choice | **Bulwark**: shields block arrows from wider angles + knockback resistance R3 · **Brawler**: +1 armour while wearing no shield, regen after taking hits R3 |
| 4 | Vitality II R3 · Fire Ward R2: −15% fire damage · Blast Ward R2: −15% explosion damage · Toughened II R3 |
| 5 | Shield Thorns II R2 · **Capstone choice**: *Second Wind* (survive a killing blow, 5 min cooldown) or *Unbreakable* (armour durability loss −50%) |

### Agility (feather)
| Tier | Nodes |
|---|---|
| 1 | Light Feet R3: −8% stamina drain (ParCool) · Soft Landing R3: −10% fall damage · Runner R2: +3% sprint speed |
| 2 | Glider R3: −10% Paragliders stamina drain · Swimmer R2: swim speed · Climber R2: faster ParCool climbing/wall-run |
| 3 choice | **Freerunner**: ParCool moves cost 20% less stamina R3 · **Sky Rider**: glider speed and stamina R3 |
| 4 | Soft Landing II R3 · Second Breath R2: stamina regenerates faster · Roll Master R2: rolls/dodges negate more damage · Light Feet II R3 |
| 5 | Runner II R2 · **Capstone choice**: *Featherfall* (no fall damage under 15 blocks) or *Tireless* (stamina drain −40% total) |

### Magic (spellbook)
| Tier | Nodes |
|---|---|
| 1 | Mana Pool R3: +15 max mana (both mods) · Focus R3: +5% spell power · Flow R2: +8% mana regen |
| 2 | Mana Saver R3: 4% spell costs no mana · Quick Casting R3: −5% cooldowns · Scroll Saver R2: 10% Iron's scroll not used |
| 3 choice | **Battlemage** (Iron's lean): +10% spell power R3 · **Artificer** (Ars lean): Ars glyph crafting/source costs −10% and familiar/summon strength R3 |
| 4 | Mana Pool II R3 · Flow II R3 · Mana Saver II R3 · Spell Shield: brief resistance after casting |
| 5 | Focus II R2 · **Capstone choice**: *Archmage* (12% spells cost no mana, −15% cooldowns) or *Wellspring* (mana regen doubled while not in combat) |

### Taming (lead)
| Tier | Nodes |
|---|---|
| 1 | Gentle Hand R3: +taming success on hard tames · Treat Saver R3: 10% taming/feeding food not used · Caretaker R2: feeding heals pets more |
| 2 | Pet Scavenging R3: pets sometimes drop found resources · Bonded R2: pets +15% health · Quick Tame R2: tames need fewer attempts |
| 3 choice | **Beastmaster** (combat pets): pets +15% damage R3 · **Shepherd** (companions): pet scavenging tier up + twins when breeding pets R3 |
| 4 | Pack Tactics R3: pets +damage on your target · Bonded II R3: armour + regen · Revive Pets R3: Pet Mementos (cost falls per rank) · Swift Paws R2: pet speed |
| 5 | Gentle Hand II R2 · **Capstone choice**: *Alpha* (pets gain +30% all stats and a chance to stun on hit) or *Kindred Spirit* (free revives and pets scavenge rare loot) |

## Skills that look thin (for discussion)

- **Woodcutting** has the least unique to do. Suggest widening it into **Foraging**: logs plus berries,
  mushrooms, flowers, beehives, catching butterflies and bugs (Bok's Butterflies, bug nets).
- **Brewing** (Let's Do Vinery/Brewery/HerbalBrews, potions) is folded into Cooking; it could be its own tree if
  Cooking feels crowded.
- **Exploring** has no tree but lots of content (dungeons, structures, waystones, compasses, boats, airships):
  a candidate 13th tree (discover structures, travel distance; perks: loot luck, waystone discounts, map
  reveal, boat/airship speed).
- **Mining tier 2** "Night Eyes" and "Hard Hat" are filler-ish; worth better ideas during the preview.

## Phases

1. **Preview trees** (this doc → config): install Pufferfish's Skills on a test branch, build all trees with
   `dummy` rewards (names, icons, descriptions, tiers, arrows, choices). Try them in a throwaway world, grant
   points with a command, iterate on layout and wording.
2. **Add-on core**: fotfskills project, perk/XP-source registration, the common perk types (save, extra
   output, speed, stats) wired into the trees. Turn on XP.
3. **Unique perks**: homing, weapon types, green thumb, scavenging, revive/Mementos, second wind, etc.
4. **Tuning and release**: balance pass on the test branch, then main.
5. Separate project: shared Ars/Iron's mana (feasibility test first).

## Testing

- Each custom XP source and perk gets an in-game check in the throwaway world (commands to set levels).
- Server log must stay free of mixin/registry errors; KubeJS and Pufferfish config load with 0 errors.
- Client install tested with packwiz-installer before pushing (CF-excluded check).

## Risks / open points

- Mod-specific hooks (Iron's casting, Ars casting, ParCool stamina, Paragliders stamina, unicorn taming) need a
  per-mod check; any that can't be hooked cleanly get a simpler stand-in perk.
- "Extra drops" must not double with Fortune/Looting exploits; tested per source.
- Pufferfish's anti-farming limits need tuning for mob farms vs normal play.
