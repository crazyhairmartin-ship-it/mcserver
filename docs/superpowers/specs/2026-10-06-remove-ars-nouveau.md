# Remove Ars Nouveau cleanly, add Obscura's Simple Storage

Status: spec only, nothing applied. Written 2026-10-06 from the repo on branch `claude/cloud-session-setup-epiuzy`, with
Ars Nouveau `ars_nouveau-1.20.1-4.12.7-all.jar` and Obscura's Simple Storage v5.0.0 checked inside their jars.

## Goal

- Take Ars Nouveau out of the pack without losing anything players care about: builds and items should turn into vanilla
  equivalents instead of air.
- Replace the one thing Ars does that nothing else in the pack covers, the **Storage Lectern network**, with
  **Obscura's Simple Storage**.
- Iron's Spells is already the only spell system (Ars spellcasting was trimmed out), so magic itself doesn't need a
  replacement.

## What Ars still does in the pack

Spellcasting is already gone: `kubejs/startup_scripts/trimmed_items.js` removes spell books, glyphs, the Scribe's Table,
turrets and the other spell items, and `kubejs/server_scripts/trim_ars.js` removes their recipes. What's left:

| Part | Used for | After removal |
|---|---|---|
| **Storage Lectern + Bookwyrms** | The pack's storage network. A lectern links nearby chests into one searchable list. fotfmail adds a creative-tab sort, "move matching" and "restock" buttons, and wandering Bookwyrms | **Obscura's Simple Storage** (below) |
| Source, sourcelinks, Source Jars, Enchanting Apparatus, Imbuement Chamber, rituals | Ars crafting and progression | Gone. Nothing needs replacing: other mods don't depend on source |
| Familiars, Starbuncles, Drygmies, Whirlisprigs, Wixies, Amethyst Golems | Farming and item-moving helpers | Gone (the mobs vanish). Obscura's hoppers and Interface cover the item moving |
| Wilden (hunter, stalker, guardian, chimera boss), Weald Walkers | Mobs, plus Wilden Dens (`ars_nouveau:wilden_den_set`) | Gone |
| Mage armour and mana enchantments | Raise the shared Iron's mana pool (fotfskills `ManaMerge`) | Gone. Iron's own gear, enchantments and the Magic tree still raise mana |
| **Archwood** (4 coloured trees, one plank type), Archwood Forest biome, sourceberry bushes, mageblooms | Worldgen and building wood | Blocks remapped to vanilla, biome kept as a datapack (below) |
| Sourcestone blocks (~90 variants) | Building blocks | Remapped to vanilla stone blocks |

## Obscura's Simple Storage (replacement for the Storage Lectern)

- **What:** Navrelis's maintained fork of Tom's Simple Storage: [CurseForge](https://www.curseforge.com/minecraft/mc-mods/obscuras-simple-storage),
  project 1475987. **CurseForge only** (not on Modrinth), so it's `packwiz cf add obscuras-simple-storage`, or a
  `.pw.toml` for file **9025722** (`obscuras_simple_storage-forge-mc1.20.1-v5.0.0.jar`, Oct 1, 2026). MIT licence.
- **How it works:** an Inventory Connector joins every chest, barrel or modded inventory touching it into one network
  (16 blocks by default, Inventory Trim bridges gaps, cables for longer runs). A Storage Terminal or Crafting Terminal
  shows everything in one list. Items stay in ordinary containers, so removing the mod later loses nothing (except
  what's in its Filing Cabinets). No power, no channels, no autocrafting.
- **It does more than the Storage Lectern:**
  - a Crafting Terminal with JEI recipe transfer (JEI support is built in)
  - wireless access
  - filters, and hoppers that work with the network
  - a Level Emitter
  - a Filing Cabinet (512 unstackable items in one block)
  - a Shulker Dock
  - a Tidy button that merges partial stacks
  - Frame Labels (an item in a glow item frame tells a chest what it should hold)
  - comparator output
  - a Network Doctor for admins to see what each network costs the server
- **Dependencies:** none beyond Forge 47.1+ and Minecraft 1.20.1 (checked in its `mods.toml`). Both sides.
- **Caveats:**
  - **Very new on Forge.** The project is from March 2026, but the Forge 1.20.1 builds only appeared on Sep 30
    (v4.0.0) and Oct 1 (v5.0.0), 2026. Before that, 1.20.1 was Fabric only. One author, ~15k downloads.
  - **v5.0.0 changed the mod id** to `obscuras_storage`. Add v5 or later straight away, so the id never changes in
    our world. If a later version renames it again, its migration notes say 4.x worlds are converted automatically.
- **Tom's Simple Storage itself** (`toms-storage`, 1.20-1.7.1 for Forge) is the alternative if the fork turns out
  unstable: same blocks, older, ~20M downloads. Re-Imagine-Tom-Simple-Storage (a vanilla-style texture pack, All
  Rights Reserved, 1.18.2–1.21.3) targets Tom's mod ids, so it **won't retexture Obscura's** blocks since v5 renamed
  them. Dropped from the plan.

### fotfmail's Storage Lectern extras

fotfmail mixes into Ars's storage classes (`extras/fotfmail/src/fotfmail/`):

| File | What it does | Plan |
|---|---|---|
| `mixin/AbstractStorageTerminalScreenMixin.java`, `mixin/StorageTerminalMenuAccessor.java`, `LecternDeposit.java`, `CreativeTabSort.java` | Creative-tab sort mode, "move matching items" and "restock" buttons on the Storage Lectern | **Port to Obscura's Storage/Crafting Terminal** (same Tom's-style terminal code, so it should be close) or drop. Obscura's own sorting and Tidy might be enough; decide after trying it |
| `mixin/EntityBookwyrmMixin.java`, `mixin/RandomStorageVisitGoalMixin.java`, `BookwyrmWanderGoal.java` | Bookwyrms flutter around their lectern network | Delete |
| `kubejs/assets/ars_nouveau/textures/gui/sort_type.png` + `kubejs/assets/ars_nouveau/lang/en_us.json` | Icon and tooltip for the creative-tab sort | Move to the new terminal's namespace if ported, otherwise delete |

`fotfmail.mixins.json` has `"required": true`, and these mixins name Ars classes directly. **Check that fotfmail
still loads without Ars before anything else.** fotfskills already does: its Ars mixins only log "Error loading
class" warnings on the test server, which has no Ars. If fotfmail crashes, remove the four Ars mixins from its
config first.

## The world: blocks, items, biome, entities

Same approach as the Tinkers removal (see issue #1): permanent **block and item aliases** in
`extras/fotfskills/src/fotfskills/world/RemovedBlocks.java`, guarded by `!ModList.get().isLoaded("ars_nouveau")`, plus
`MissingMappingsEvent` remaps for the first boot. Rebuild and deploy fotfskills **before** Ars is removed.

**Proposed block mapping** (open to change):

| Ars blocks | Vanilla replacement |
|---|---|
| Archwood logs, wood, stripped logs/wood (red, blue, green, purple) | Suggested by colour: **red → crimson stem, blue → warped stem, green → jungle log, purple → dark oak log** (decide) |
| Archwood planks, slab, stairs, fence, gate, door, trapdoor, button, pressure plate, signs | Matching set of the plank choice above (one plank type, so pick one: dark oak suggested) |
| Archwood leaves (4 colours) | Cherry / azalea / jungle / flowering azalea leaves by colour (decide) |
| Archwood saplings (and potted) | Matching vanilla sapling |
| Archwood Chest | Chest (see block entities below) |
| Sourcestone, smooth and gilded sourcestone (every pattern, slab, stairs) | Stone bricks / polished andesite / chiseled stone bricks; slabs and stairs to the matching shape |
| Sconces, Magelight Torch, light blocks | Lantern / torch / air for the invisible light blocks |
| Sourceberry bush | Sweet berry bush |
| Magebloom crop and block | Wheat (age kept) / pink wool or moss |
| Bastion, bombegranate, frostaya, mendosteen pods | Cocoa or air |
| Falseweave, ghostweave, mirrorweave, sky block, mage block | Glass / white wool |
| Machines (Enchanting Apparatus, Arcane Core, pedestals, Imbuement Chamber, Alteration Table, Source/Potion/Mob Jars, relays, sourcelinks, Storage/Bookwyrm Lectern, Ritual Brazier, Crystallizer, Wixie Cauldron, Scryer's blocks, Drygmy Stone, Repository) | A vanilla look-alike (e.g. lectern → lectern, cauldron → cauldron, jars → glass, rest → smooth stone or chiseled stone bricks) |
| Turrets, runes, prisms, spell sensor, temporary/redstone/intangible air, portals, magic fire | Air |

**Items** (inventories, chests, backpacks): source gem → amethyst shard; source gem block → amethyst block; archwood and
sourcestone block items follow the block table; magebloom → pink dye or wheat; sourceberries → sweet berries;
everything else (mage armour, familiar items, wands, jars...) disappears. **Mage armour is the big loss**: warn players.

**Block entities, where items are lost.** An alias swaps the block, but the block's contents are saved under Ars's
block-entity id. Without Ars those contents are dropped on load:
- Archwood Chests and Repositories (chest-style storage)
- Source Jars, Potion Jars, **Mob Jars** (captured mobs)
- items sitting on pedestals and in Imbuement Chambers or Alteration Tables

Choose one:
- [ ] **Tell players to empty these** before the update (simplest).
- [ ] _Or_ also rewrite block-entity ids when chunks load (`ars_nouveau:archwood_chest` and `repository` →
  `minecraft:chest`, keeping `Items`) in fotfskills, next to the aliases. That's more code, but nothing in a chest is lost.

**Archwood Forest biome.** Ars adds `ars_nouveau:archwood_forest` through TerraBlender (`archwoodForest = 2` in
`config/ars_nouveau-common.toml`), so it's saved in the world's chunks. Without Ars that id is unknown and those chunks
log errors and fall back to a default biome. **Keep the id alive with a datapack**: add
`kubejs/data/ars_nouveau/worldgen/biome/archwood_forest.json`, a copy of vanilla `forest` (same climate, colours and
spawns; no archwood features). Datapacks may define biomes in any namespace, and TerraBlender won't place it in new
chunks, so it only keeps existing forests valid.

**Entities.** Starbuncles, Bookwyrms, Drygmies, Whirlisprigs, Wixies, Amethyst Golems, familiars, Wilden and Weald
Walkers are removed when their chunks load (one log line each). Nothing to do, but **warn players about tamed
helpers**.

**Structures.** Wilden Den starts in chunks reference a structure that no longer exists; Minecraft logs and drops them.
The dens' blocks stay and convert through the aliases.

The unexplored-chunk reset (issue #1) wipes Ars worldgen from every unvisited chunk anyway, so the mapping matters
most around bases and paths.

## fotfskills changes

fotfskills already runs without Ars: every Ars hook is behind `ModList.get().isLoaded("ars_nouveau")` or a mixin that
just doesn't apply. So removal won't crash it. Tidy-up, in the same rebuild as the aliases:

- [ ] **Delete:** `perk/ArsMana.java`, `perk/ArsPerks.java`, `perk/SourcePerks.java`, the Ars mixins
  (`ArsApparatusMixin`, `ArsManaCapMixin`, `ArsManaHudMixin`, `ArsManaRegenMixin`, `ArsSourcelinkMixin`,
  `ArsSpellResolverMixin`, `ScribesTableMixin`) and their entries in `res/fotfskills.mixins.json`.
- [ ] **Shared mana:** `mana/ManaMerge.java`, `ManaMergeTicker.java` and `ManaMath.java` only switch on when both Ars and
  Iron's are installed. Delete them, plus the `sharedMana` block in `FotfSkills.java`. Iron's mana stays the pool, as
  it is today. Also drop the shared-mana test cases (`ManaMathTest`).
- [ ] **`FotfSkills.java`:** remove the `ars_nouveau` registrations (ArsPerks, SourcePerks, the `ModSummons::ars`
  summon owner, `Mana.register(ArsMana::add)`).
- [ ] **`perk/ModSummons.java` and `pet/Ferality.java`:** drop the Ars summon interface.
- [ ] **`perk/ItemPerks.java`:** Spellwright counts `irons_spellbooks` only.
- [ ] **Tags:** remove `ars_nouveau:` entries from `res/data/fotfskills/tags/` (`items/magic.json`, `bow.json`,
  `crossbow.json`, `sword.json`, `blocks/wild_plants.json`, `worldgen/biome/forests.json`). They're optional entries,
  so harmless, but tidy.

**Skill tree** (`config/puffish_skills/categories/magic/definitions.json` and `craft/definitions.json`):
- [ ] **Sourcecraft I–III** (sourcelinks and the enchanting apparatus) has nothing left to do. Replace it with an
  Iron's perk, e.g. cheaper Alchemist Cauldron brewing, more Arcane Essence, or faster scroll crafting.
- [ ] **Mana Saver I–IV and Archmage** (`free_spell` roll) and **Druid's Grove / Wellspring**: check their Iron's
  paths in `IronsPerks` still cover them. If a node only did something for Ars, re-point or replace it.
- [ ] **Summoner I–III:** the text says "(Iron's and Ars)". Change it to Iron's only.
- [ ] **Spellwright I–III** (craft tree): the text says "Iron's scrolls and Ars items". Change it to Iron's only.
- [ ] Regenerate the trees and icons (`tools/skills/trees.json`, `tools/skills/icons.json` has 1 Ars icon), and the design
  docs if wanted (`docs/superpowers/specs/2026-10-03-skills-design.md`, `skill-trees.html`,
  `2026-10-04-shared-mana-design.md`).
- [ ] Players who spent points on removed or changed nodes: offer a respec (Pufferfish's Skills reset command) after the update.

## Everything else in the repo that references Ars

- [ ] `mods/ars-nouveau.pw.toml`: `packwiz remove ars-nouveau`. No other mod in the pack requires it.
- [ ] `config/ars_nouveau-common.toml`: delete.
- [ ] `kubejs/server_scripts/trim_ars.js`: delete. `kubejs/startup_scripts/trimmed_items.js`: remove the Ars block (~108 `ars_nouveau:` entries).
- [ ] `kubejs/server_scripts/field_guide.js`: the `ars: () => Item.of('ars_nouveau:worn_notebook')` entry (`/guide ars`). Repoint to a `/guide storage` page for Obscura's or drop it.
- [ ] `patchouli_books/fotf_field_guide/en_us/entries/magic/ars_nouveau.json`: delete; `magic/which_magic.json` and `getting_started/books.json`: remove Ars mentions. Add a **storage** page for Obscura's (connector, terminal, crafting terminal, Frame Labels) next to `getting_started/storage.json`.
- [ ] `patchouli_books/fotf_cookbook/.../ars_nouveau__source_berry_pie.json`, `..._roll.json`: delete, and regenerate the cookbook (`tools/cookbook/make_cookbook.py`, `food_dump.json`).
- [ ] **Mailboxes in archwood:** `kubejs/startup_scripts/mailbox_woods.js`, `tools/mailbox/woods.json` (`ars_nouveau_archwood`), fotfmail's generated `MailboxWood.java` (regenerate with `tools/mailbox/make_mailbox.py`), and the Ender Mail archwood locker models (`kubejs/assets/endermail/models/block/locker_ars_nouveau_archwood*.json`, `blockstates/locker.json`, `models/item/locker.json`). Placed archwood mailboxes need an alias to another wood's mailbox.
- [ ] `tools/archwood/` (recolour tool): delete.
- [ ] `config/everycomp-entries.toml`: the `[types.wood_type.ars_nouveau]` and `[types.leaves_type.ars_nouveau]` sections. Every Compat's archwood variants of other mods' blocks disappear too; alias any that were placed.
- [ ] `config/defaultoptions/keybindings.txt`: the `key_key.ars_nouveau.*` lines (all unbound already).
- [ ] `config/inventoryprofilesnext/integrationHints/endermail.json`: check the Ars reference.
- [ ] `tools/make_field_guide.py`, `tools/testkit/make_test_datapack.py`, `tools/names/names.json`, `tools/names/managed_keys.json`: drop Ars entries.
- [ ] `docs/superpowers/specs/2026-10-03-weapons.csv` and the plan docs: leave as history, or note Ars was removed.
- [ ] Run `packwiz refresh`.

## Order

1. Build and deploy the **new fotfskills** (aliases, remaps, optionally the block-entity rewrite, Ars code removed, new
   Sourcecraft replacement) and the **biome datapack**. Fix or update **fotfmail** (Ars mixins out, terminal extras
   ported or dropped).
2. Add **Obscura's Simple Storage** one update early if possible, so players can rebuild their storage rooms while the
   Storage Lectern still works and move items over themselves.
3. Warn players: mage armour, familiars and Ars helpers go; empty Archwood Chests, Repositories and jars (unless the
   block-entity rewrite is built); storage lecterns become plain lecterns, but **items in linked chests stay**.
4. In the update downtime, **back up the world**, remove Ars, start the server and check the log for unknown blocks,
   items or biomes.
5. Respec offer for changed Magic nodes.

## Test on a copy of the server world

- [ ] Server and client start with Ars removed, the new fotfskills and fotfmail, and Obscura's.
- [ ] An archwood forest, a sourcestone build and an Ars machine room convert to the chosen vanilla blocks with the right
  shapes (stairs, slabs, logs).
- [ ] The Archwood Forest biome still loads (no biome errors), with forest colours and grass.
- [ ] Chests that were linked to a Storage Lectern still hold their items. An Obscura's connector and terminal on them
  show everything.
- [ ] Archwood Chest / Repository contents: lost as expected, or kept if the block-entity rewrite was built.
- [ ] Inventories and backpacks: source gems became amethyst shards, and unmapped Ars items are gone without errors.
- [ ] The Magic tree loads, the replaced nodes work, and Iron's mana is unchanged for a player without Ars gear.
- [ ] An archwood mailbox converts to the chosen replacement wood's mailbox.
