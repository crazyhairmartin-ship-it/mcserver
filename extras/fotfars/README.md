# Friends of the Forest Ars

Small Forge add-on for Ars Nouveau (both sides). These tweaks used to live in fotfmail; they're separate so fotfmail
doesn't depend on Ars, and so this mod can simply be dropped if Ars ever leaves the pack.

- **Creative-tab sort for the Storage Lectern.** A third sort mode after amount and name: items in creative
  inventory order (`CreativeTabSort`, client mixin on Ars Nouveau's `AbstractStorageTerminalScreen`). Its icon
  is the third tile of `kubejs/assets/ars_nouveau/textures/gui/sort_type.png`; tooltip in that folder's lang.
- **Bookwyrms flutter around.** Ars Nouveau's Bookwyrms only move to transfer items or hover at a random chest.
  `BookwyrmWanderGoal` (added by mixin on `EntityBookwyrm.registerGoals`) has idle ones fly between open spots
  around their lectern network now and then, sometimes hovering over a connected lectern (their own plus any
  lecterns linked to it), only where they can actually fly. Ars's chest visits are cut to about 1 in 5 of the
  times they'd start (`RandomStorageVisitGoalMixin`) so the wander gets a turn.
- **Move matching items into / restock from the Storage Lectern.** Two purple side tabs above the lectern's own
  (`AbstractStorageTerminalScreenMixin`, icons `textures/gui/lectern_*.png`, drawn by `draw_icons.py`) send `LecternDeposit`: up arrow puts
  main-inventory stacks whose item is already stored in via `pushStack`; down arrow tops up every partial stack
  (hotbar included) via `pullStack`. IPN's buttons are hidden on the lectern (config/inventoryprofilesnext/
  integrationHints/endermail.json), since they can't reach its virtual slots.

Rebuild the jar with `./build.sh` (Docker, JDK 17 container). Compiled against Forge's SRG-named Minecraft jar without
Gradle, so vanilla methods are written as `m_XXXX_` and mixins use `remap = false`.
