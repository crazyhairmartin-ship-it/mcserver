# Friends of the Forest Mail

Small Forge add-on for Ender Mail (both sides).

- **Mailboxes in every wood.** Adds a `wood` block state to Ender Mail's locker (shown as a birdhouse "Mailbox"
  by `kubejs/assets/endermail`). The crafting recipe's planks set it (item NBT `BlockStateTag.wood`, see
  `kubejs/server_scripts/mail_recipes.js`), and breaking the mailbox keeps it (loot table `copy_state`).
- **Letters.** `fotfmail:letter`: write on it like a book and quill, sign it with the recipient's mailbox ID as
  the title, then right-click any mailbox to deliver it straight into theirs (searches every dimension).
  A signed letter stays the same item and opens as a readable book.

The wood list comes from `tools/mailbox/woods.json`; `tools/mailbox/make_mailbox.py` regenerates
`src/fotfmail/MailboxWood.java` and every mailbox model, blockstate and recipe list together. Rebuild the jar with
`./build.sh` (Docker, JDK 17 container). Bump the version in the filename, `mods.toml`, `MANIFEST.MF` and
`mods/fotfmail.pw.toml` (url + sha512) if you change it. Icons: `draw_icons.py`.

Compiled against Forge's SRG-named Minecraft jar without Gradle, so vanilla methods are written as `m_XXXX_`
and mixins use `remap = false`. Mixins: `LockerBlock.createBlockStateDefinition` (adds `wood`) and
`ServerGamePacketListenerImpl.updateBookContents/signBook` (saves and signs letters like writable books).
