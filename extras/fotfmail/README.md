# Friends of the Forest Mail

Small Forge add-on for Ender Mail and Domestication Innovation (both sides).

- **Mailboxes in every wood.** Adds a `wood` block state to Ender Mail's locker (shown as a birdhouse "Mailbox"
  by `kubejs/assets/endermail`). The crafting recipe's planks set it (item NBT `BlockStateTag.wood`, see
  `kubejs/server_scripts/mail_recipes.js`), and breaking the mailbox keeps it (loot table `copy_state`).
- **Letters.** `fotfmail:letter`: write on it like a book and quill, sign it with the recipient's mailbox ID as
  the title, then right-click any mailbox. One of Ender Mail's mail carriers (wearing a mail cap, see
  `MailHatLayer`) appears 8-12 blocks from that mailbox in a random direction, walks up, takes the letter, walks off and
  teleports; then appears in front of the friend's mailbox, walks up, drops the letter in, walks away and
  teleports out (`CarrierGoal`; Ender Mail's own carrier goals and random teleports are off for these carriers).
  If nobody is near the friend's mailbox it's delivered straight in. Other dimensions get it instantly.
  A signed letter stays the same item and opens as a readable book.
- **Collar effects on GeckoLib pets.** Domestication Innovation only draws its collar enchantment effects
  (shadow hands, magnet, auras, blazing bars...) on vanilla-style renderers, so Critters & Companions,
  Naturalist and unicorn-mod pets showed nothing. `PetOverlaysGeoLayer` runs DI's own `LayerPetOverlays` from a
  GeckoLib render layer on every GeoEntityRenderer. The immunity-frame glint and zombie-pet overlay redraw a
  vanilla model, so those two stay off on GeckoLib mobs.
  Shadow Hands and Blazing Protection bars (the two DI draws all the time) only show while the pet is
  fighting or was just hurt, then linger 5 seconds (`CollarEffectTiming`, client mixin on `LayerPetOverlays`).
- **Creative-tab sort for the Storage Lectern.** A third sort mode after amount and name: items in creative
  inventory order (`CreativeTabSort`, client mixin on Ars Nouveau's `AbstractStorageTerminalScreen`). Its icon
  is the third tile of `kubejs/assets/ars_nouveau/textures/gui/sort_type.png`; tooltip in that folder's lang.
- **Bookwyrms flutter around.** Ars Nouveau's Bookwyrms only move to transfer items or hover at a random chest.
  `BookwyrmWanderGoal` (added by mixin on `EntityBookwyrm.registerGoals`) has idle ones fly between open spots
  around their lectern network now and then, sometimes hovering over a connected lectern (their own plus any
  lecterns linked to it), only where they can actually fly. Ars's chest visits are cut to about 1 in 5 of the
  times they'd start (`RandomStorageVisitGoalMixin`) so the wander gets a turn.
- **Nightmare hoof fire burns out about 3x sooner** (`NightmareFireBlockMixin`, Ultimate Unicorn Mod).
- **Ender Mail carriers are invulnerable** (rain and water used to hurt them).

The wood list comes from `tools/mailbox/woods.json`; `tools/mailbox/make_mailbox.py` regenerates
`src/fotfmail/MailboxWood.java` and every mailbox model, blockstate and recipe list together. Rebuild the jar with
`./build.sh` (Docker, JDK 17 container). Bump the version in the filename, `mods.toml`, `MANIFEST.MF` and
`mods/fotfmail.pw.toml` (url + sha512) if you change it.

Compiled against Forge's SRG-named Minecraft jar without Gradle, so vanilla methods are written as `m_XXXX_`
and mixins use `remap = false`. Mixins: `LockerBlock.createBlockStateDefinition` (adds `wood`),
`ServerGamePacketListenerImpl.updateBookContents/signBook` (saves and signs letters like writable books) and
`EnderMailmanEntity.getPackageStack` (carriers flagged `fotfmail_letter` hand over the letter itself).
Icons and the hat texture: `draw_icons.py`.
