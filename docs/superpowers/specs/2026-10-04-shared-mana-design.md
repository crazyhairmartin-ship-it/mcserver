# Shared mana: Ars Nouveau + Iron's Spells

Status: design approved in chat by Dylan (2026-10-04): pool size "base of one, bonuses from both", Iron's bar, approach 1. Built on branch `mana-merge`.

## Goal

Dylan: "I really wish there was a way we could make both mods' mana effects combine." There is one mana pool:
- Every spell from either mod draws from it.
- Every mana bonus from either mod (gear, enchantments, glyphs, book tiers, rings, skills) raises it.

## Decisions

- **Pool size.** The pool starts at Iron's base of 100. Iron's own max-mana bonuses apply as normal. Ars's bonuses above its own base of 100 are added on top:
  - glyphs known
  - book tier
  - Mana Boost enchantment
  - Ars max-mana gear and attributes
- **Bar.** Iron's mana bar shows the pool. Ars's mana HUD is hidden; the spell book and its other UI stay.
- **Approach 1: Iron's mana is the pool.**
  - Ars's mana capability is redirected on the server: current mana, set mana and max mana read and write Iron's MagicData and Iron's max mana. Ars's add and remove go through set, so they are covered too.
  - Ars syncs its client copy from the redirected values, so its spell book shows the shared numbers.
- **One regen.** Ars's own regen (`ManaUtil.getManaRegen`, mana per second) returns 0 for players. The part above Ars's base regen becomes an Iron's mana-regen bonus that gives the same mana per second:
  - book tier
  - glyphs
  - Mana Regen enchantment
  - gear

  Iron's regen adds `max x 0.01 x regen x manaRegenMultiplier` every 10 ticks, so +1 mana per second needs +1 / (max x 0.02 x multiplier) regen.
- **Skills tree.**
  - Mana Pool I/II give +10 to Iron's max mana only. The Ars +10 would now count twice.
  - Wellspring's Ars regen hook is off, because Iron's Wellspring covers the pool.
  - The add-on's give-mana and spend-mana helpers use only the Iron's side, because it is one pool.
  - Magic XP is unchanged: each mod's casts count their own spend once.
- **Activation.** The merge is active whenever both mods are installed. Every hook is a no-op if either mod is missing.

## Edge cases

- **Respawn and clone.** Ars copies mana to the new player through set mana, which now writes Iron's mana. Iron's `manaSpawnPercent` (0) still applies to Iron's own respawn. Whichever runs last wins; this is checked in game.
- **Gear swaps** recompute the bonus every second. Iron's setMana clamps current mana to the new max.
- **Ars reserved mana** (familiars) is already inside Ars's computed max, so it lowers the Ars bonus.
- **Creative mode** keeps each mod's own creative rules.
- **Client side:** only the server cap is redirected. The client cap holds the synced shared values.

## After review (2026-10-04)

- **Ars regen counts twice.** Ars applies its per-second regen on both tick phases, so the conversion doubles the extra to keep the same real mana per second.
- **Bonuses on login and respawn.** They are applied immediately, so nothing clamps the pool to the smaller max before the first refresh.
- **No-change writes don't clamp.** Ars calls add mana with 0 every few ticks; that no longer clamps the pool.
- **Ars's own max** is recorded where Ars calculates it.
- **Known, accepted for now:**
  - Death and leaving the End empty the pool (Iron's `manaSpawnPercent` 0). This is Iron's rule.
  - Ars's spell book cost bar shows Ars's own max, not the pool's.
  - Wellspring doesn't multiply the converted Ars regen bonus.
  - Familiar reserve below Ars's base costs nothing.
  - Iron's bar can lag after an Ars refill that lands exactly on max.
  - With a full pool and an Ars book in hand, no bar shows (Iron's "contextual" bar setting).

## Testing

- A pure unit test covers the bonus and regen conversion math (ManaMath).
- The pytest suite checks that Mana Pool is Iron's-only.
- The test server boot must show no mixin errors (the Ars hooks are `@Pseudo`, and both mods are present).
- In game:
  - casting an Ars spell lowers Iron's bar
  - an Ars book tier raises Iron's max
  - only one bar shows
  - regen happens once
