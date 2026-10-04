# Shared Mana Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** One mana pool for Ars Nouveau and Iron's Spells. Iron's mana is the pool, and Ars's bonuses add to it.

**Architecture:**
- **`fotfskills.mana`** holds `ManaMerge` (state and activation), `ManaMath` (pure conversion math), the server ticker (`ManaMergeTicker`) and the bridges.
- **Mixins:**
  - `ArsManaCapMixin` redirects Ars's ManaCap current, set and max mana to Iron's, and records Ars's computed max.
  - `ArsManaRegenMixin` captures and zeroes `ManaUtil.getManaRegen` for players.
  - `ArsManaHudMixin` (client) returns false from `GuiManaHUD.shouldDisplayBar`.
- **Skills changes:** Mana Pool becomes Iron's-only, the Ars mana bridges go when merged, and the Ars side of Wellspring goes when merged.

**Tech Stack:** Java 17 javac in Docker (SRG, remap=false), Ars Nouveau 4.12.7 and Iron's 3.16.3 classes, pytest.

**Spec:** `docs/superpowers/specs/2026-10-04-shared-mana-design.md`

## Global Constraints

- Iron's mana is the only pool when both mods are loaded. Every hook does nothing when either mod is missing.
- Only the server-side cap is redirected (the player is a ServerPlayer).
- The pool starts at Iron's base. The Ars bonus is Ars's computed max minus Ars's `INIT_MAX_MANA` config, never negative.
- Ars regen above `INIT_MANA_REGEN` converts to an Iron's mana-regen bonus that gives the same mana per second.

## Review Focus

1. **No double regen** (Ars regen zeroed), and no double max (Mana Pool counted once).
2. **No recursion or NPE.** The ManaCap redirect must handle a non-player LivingEntity (mobs with Ars caps) by leaving the original behaviour.
3. **Client copy.** Ars's client cap still receives sane values; the HUD is hidden only when Iron's is present.
4. **Respawn and dimension change** don't zero or duplicate mana unexpectedly.

---

### Task 1: ManaMath (pure)

- [ ] **Step 1: Write the failing test** (`extras/fotfskills/test/fotfskills/mana/ManaMathTest.java`):

```java
package fotfskills.mana;

/** Shared mana conversions. Run: sh test.sh */
public final class ManaMathTest {
    public static void main(String[] args) {
        check(ManaMath.maxBonus(100, 100) == 0, "Ars at its base adds nothing");
        check(ManaMath.maxBonus(265, 100) == 165, "glyphs, book tier and gear above Ars's base add to the pool");
        check(ManaMath.maxBonus(80, 100) == 0, "never negative (reserved mana)");
        // Iron's regen: max x 0.02 x regen x multiplier per second. 2 mana/s extra on a 200 pool at x1 -> +0.5 regen
        check(Math.abs(ManaMath.regenBonus(7, 5, 200, 1.0) - 0.5) < 1e-9, "Ars regen above its base becomes Iron's regen");
        check(ManaMath.regenBonus(5, 5, 200, 1.0) == 0, "Ars base regen adds nothing (Iron's own regen is the base)");
        check(ManaMath.regenBonus(9, 5, 0, 1.0) == 0, "no pool, no division by zero");
        System.out.println("ManaMathTest ok");
    }

    private static void check(boolean ok, String what) {
        if (!ok) { System.out.println("FAIL: " + what); System.exit(1); }
    }
}
```

- [ ] **Step 2: Run the test.** It is expected to FAIL.
- [ ] **Step 3: Implement** `ManaMath.maxBonus(int arsMax, int arsBase)` and `ManaMath.regenBonus(double arsRegenPerSecond, double arsBaseRegen, double ironsMax, double multiplier)`.
- [ ] **Step 4: Run the test.** It is expected to pass.
- [ ] **Step 5: Commit.**

### Task 2: Merge hooks

- **`IronsMana`:** add `get(player)`, `max(player)` and `set(player, value)` (clamped).
- **`ManaMerge`:**
  - `ACTIVE`, set in the FotfSkills constructor when both mods are loaded.
  - Per-player `arsMax` and `arsRegen` maps, recorded by the mixins.
  - `ironsAvailable()`.
- **`ArsManaCapMixin`** (`@Pseudo`, targets `com.hollingsworth.arsnouveau.common.capability.ManaCap`, shadows `livingEntity`). For a ServerPlayer while ACTIVE:
  - `getCurrentMana` returns Iron's mana.
  - `setMana` sets Iron's mana (clamped) and returns it.
  - `getMaxMana` returns Iron's max.
  - `setMaxMana` records Ars's computed max, then runs normally.
- **`ArsManaRegenMixin`** (`@Pseudo`, targets `com.hollingsworth.arsnouveau.api.util.ManaUtil`): at the RETURN of `getManaRegen(Player)` for a ServerPlayer while ACTIVE, record the value and return 0.
- **`ArsManaHudMixin`** (`@Pseudo`, client list, targets `com.hollingsworth.arsnouveau.client.gui.GuiManaHUD`): `shouldDisplayBar` returns false while Iron's is loaded.
- **`ManaMergeTicker`:** every 20 ticks per player while ACTIVE:
  - `Modifiers.set(irons max_mana, "ars_max_bonus", maxBonus, ADDITION)`
  - `Modifiers.set(irons mana_regen, "ars_regen_bonus", regenBonus, ADDITION)`
  - The bases come from Ars `ServerConfig.INIT_MAX_MANA` / `INIT_MANA_REGEN` and the multiplier from Iron's `ServerConfigs.MANA_REGEN_MULTIPLIER`.
- **Wiring:**
  - `FotfSkills` registers the Ars mana bridges only when not ACTIVE.
  - `ArsPerks.onRegen` (Wellspring) returns early when ACTIVE.
- Build, test and commit.

### Task 3: Skills data

- [ ] **Step 1: Failing pytest.** Mana Pool rewards are Iron's `max_mana` only (no `ars_nouveau:` attribute).
- [ ] **Step 2: Edit `perks.json`** (mana_pool, mana_pool_ii), regenerate, run pytest, commit.

### Task 4: Ship and boot

- Update the jar hash, run `packwiz refresh`, push `mana-merge`, and boot the test server with `PACK_REF=<sha>`.
- Check that the config loaded and there are no mixin errors.
