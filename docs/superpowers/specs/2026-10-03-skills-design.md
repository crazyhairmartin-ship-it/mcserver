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
| Foraging | Chopping natural logs (incl. modded trees), picking berries and wild crops, gathering mushrooms and flowers, harvesting honey, catching butterflies and bugs |
| Farming | Harvesting fully grown crops; breeding farm animals |
| Fishing | Any catch (Aquaculture included) |
| Cooking | Finished meals: Farmer's Delight pots, Let's Do recipes, smoker/furnace food |
| Crafting | Crafting tools/armour/weapons/gear; smithing-table upgrades; smelting ingots |
| Attack | Landed melee hits, by damage dealt |
| Range | Landed projectile hits (thrown weapons too), more at long range |
| Defense | Hits taken from mobs (damage absorbed) and hits blocked with a shield (full credit) |
| Agility | ParCool moves (wall-run, climb, roll, vault, dodge), sprinting, grappling-hook swinging |
| Magic | Casting spells in either mod, by mana spent |
| Taming | Taming (rare animals worth more), feeding/healing pets, your pets landing hits |

Anti-farming: built-in per-mob and per-chunk limits; player-placed blocks give no Mining/Foraging XP;
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
projectile range (velocity), cooking-pot speed, ParCool stamina drain, grappling-hook range/speed, less fall damage,
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
- *Cheaper revival*: Taming's Soul Mender lowers the cost of the standalone pet revival (below).

## Tree drafts

The trees live in `2026-10-03-skill-trees.html` next to this doc (the `TREES` data in its script is the source of
truth; published as the "FOTF Skill Trees" artifact). Revision 2 (2026-10-03, Dylan's feedback):

- Fewer flat "+% to this skill" nodes; each tree has 3-9 **cross-skill** nodes (marked "feeds <skill>"), e.g.
  Woodcutting's Axe Mastery and Splitting Blow feed Attack, Defense's Warded Mind and Battlemage Plate feed
  Magic, Cooking's Well Fed (damage at full hunger), Farming's scythe line (Reaper, Grim Harvest, Reaper's Due),
  Agility's jump height, quicker casting, light and thrown weapons.
- Taming leans on breeding: Selective Breeding (babies take the better parent's stats), Breeder (twins, faster
  growth), Bloodlines (rare variants), Husbandry (more drops from domesticated animals), Prized Stock capstone
  (stats above the normal max). Only one node (Gentle Hand) is about tame speed/odds.
- Magic gets **Mana Shield**: with no shield equipped, blocking raises a mana barrier that works like a shield
  and spends mana per hit; Arcane Aegis makes it reflect damage.
- Heartwood (rare log drop) was cut.
- Totals: 43-46 points to fill a tree (choices counted once).

## Decisions from revision 3

- **Woodcutting is now Foraging**: logs plus berries, mushrooms, flowers, herbs, honey and bug catching
  (nodes: Berry Picker, Bug Catcher, Wildcrafter, Beekeeper, Nature's Bounty capstone).
- **No Exploring tree.** Brewing stays inside Cooking.
- **Grappling hook (Grappling Hook - Reforged)**: keep only the basic grappling hook. Remove every other hook
  item (motor, double motor, ender, magnet, rocket, smart, rocket/double variants, launcher, repeller, the
  boots) and all upgrade items plus the modifier block (recipes removed, hidden in JEI). The upgrades come back
  as Agility nodes applied per player by the add-on: Long Rope / Long Rope II (range), Hookmaster (throw, reel,
  swing), Motor Reel (pull to the hook), Twin Hooks capstone (double hook). ParCool's grapple stays unused.
  New item model and texture for the hook (separate small task).
- **Paragliders is removed** (gliders, goddess statues, spirit orbs, heart containers, stamina vessels). Its
  health and stamina growth moves to **overall level**: total of all 12 skill levels (max 600); every 40 total
  levels gives +1 heart and +5% ParCool max stamina (up to +15 hearts at 600). Do the removal in the same
  release as skills so nobody loses their spirit-gem hearts in between. Statues already placed in the world
  disappear with the mod.
- **Tree reset**: a player can reset one tree and get its points back, paying XP levels: 1 level per 2 points
  spent, minimum 5 (a player command or button from the add-on, calling Pufferfish's Category API reset;
  Pufferfish's own commands need operator permission).

## Decisions from revision 4

- **ParCool**: every action has learn cost 0 (done in the pack, `defaultconfigs/parcool-server.toml`); its skill
  tree key is unbound by default. Agility perks only scale stamina, not unlocks.
- **Overall level hearts follow a gentle curve** (rev 5; exponential was too steep): each step gives +1 heart and
  +5% ParCool stamina; step k of 15 needs 256 x (k/15)^1.3 total levels (all 15 hearts by total level 256): 8, 19, 32, 46, 61, 78, 95, 113, 132, 151, 171, 192, 213, 234, 256.
- **Crafting power is guaranteed, not a roll**: Enchanted Crafts always adds a random enchantment (level I, up to
  II, up to III by rank); Enchanted Crafts II raises the level; Weaponsmith always +1 attack damage; Armourer
  always +1 toughness; Masterwork always two enchantments. Resource-saving perks (Frugal, Endless Workshop)
  stay as chances.
- **Point costs**: all capstones, Weaponsmith and Armourer are single nodes costing 3 points. Other nodes cost
  1 point per rank.
- New/changed nodes: Loyal Guard (Taming: a nearby pet blocks a hit, no damage to you or the pet), Multishot
  (Range, replaces Crossbowman; Steady Hands and Rapid Volley also speed up crossbow reload), Staff Adept (Magic:
  spell power and cooldowns while holding a staff or wand), Long Net
  (Foraging: net reach, since net catches never fail), Brain Food (+mana regen after meals), Picnic heals you
  too, Guardian covers party members and pets.
- **Weapon types**: every weapon in the pack is classified into sword, light, two-handed, polearm, axe, blunt,
  scythe, thrown, bow, crossbow (the three firearms count as crossbows) and magic (`2026-10-03-weapons.csv`, 671 weapons from 20 mods,
  trimmed items excluded). The add-on ships these as item tags (`fotfskills:<type>`) so every mod's weapons
  get the matching perks; the CSV is reviewed and hand-corrected before release.
- Numbers are still rough; a tuning pass happens in the preview. Damage note (approved design, 2026-10-03):
  percent bonuses scale with weapon size (+15% is 2.4 damage on a 16-damage two-hander but 0.6 on a 4-damage
  dagger), so early damage nodes use flat bonuses (+0.5 to +1 damage) and percent bonuses are kept for
  big-weapon branches; values are checked against real hits in the preview world.

## Pet revival (standalone, not a perk)

Everyone has it, skills or not. A tamed animal or owned companion that dies leaves a **Pet Memento** item at
its death spot (also sent to the owner if they're far away) holding the whole pet: name, collar enchantments,
armour, saddle, stats and variant. Using the Memento brings the pet back after a base cost (an item such as a
golden apple or a Pet Memento-specific recipe, plus a short wait). Taming's Soul Mender cuts the cost 25% per
rank. Lives in the FOTF Skills add-on but works without Pufferfish's Skills. Exact cost decided in the preview.

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
