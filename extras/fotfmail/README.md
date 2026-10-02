# Friends of the Forest Mail

Small Forge add-on for Ender Mail (both sides).

- **Mailboxes in every wood.** Adds a `wood` block state to Ender Mail's locker (shown as a birdhouse "Mailbox"
  by `kubejs/assets/endermail`). The crafting recipe's planks set it (item NBT `BlockStateTag.wood`, see
  `kubejs/server_scripts/mail_recipes.js`), and breaking the mailbox keeps it (loot table `copy_state`).
- **Letters.** `fotfmail:letter`: write on it like a book and quill, sign it with the recipient's mailbox ID as
  the title, then right-click any mailbox. One of Ender Mail's mail carriers (wearing a mail cap, see
  `MailHatLayer`) appears already holding it, teleports to the friend's mailbox about 5 seconds later and drops
  the letter itself in (not wrapped in a package). Mailboxes in other dimensions get it instantly.
  A signed letter stays the same item and opens as a readable book.

The wood list comes from `tools/mailbox/woods.json`; `tools/mailbox/make_mailbox.py` regenerates
`src/fotfmail/MailboxWood.java` and every mailbox model, blockstate and recipe list together. Rebuild the jar with
`./build.sh` (Docker, JDK 17 container). Bump the version in the filename, `mods.toml`, `MANIFEST.MF` and
`mods/fotfmail.pw.toml` (url + sha512) if you change it.

Compiled against Forge's SRG-named Minecraft jar without Gradle, so vanilla methods are written as `m_XXXX_`
and mixins use `remap = false`. Mixins: `LockerBlock.createBlockStateDefinition` (adds `wood`),
`ServerGamePacketListenerImpl.updateBookContents/signBook` (saves and signs letters like writable books) and
`EnderMailmanEntity.getPackageStack` (carriers flagged `fotfmail_letter` hand over the letter itself).
Icons and the hat texture: `draw_icons.py`.
