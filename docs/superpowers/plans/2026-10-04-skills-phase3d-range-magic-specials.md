# Skills Phase 3d: Range, Defense and Magic Specials Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Wire the last perk nodes of phase 3. These are:

| Tree | Nodes |
|---|---|
| Range | Homing Arrows, Seeker, Multishot, Arcane Arrows, Retriever |
| Defense | Shield Wall, Bulwark |
| Magic | Mana Shield, Arcane Aegis, Scroll Saver, Wellspring, Druid's Grove (Foraging) |
| Melee | Earthshaker (Mining), Reaper's Due (Farming) |

**Architecture:** The work lives in a few classes:

- **`RangePerks`** handles player arrows when they enter the world: homing tracking, Seeker crits, Multishot clones, and Arcane Arrows mana marks. It also handles impacts (Retriever) and arrow damage (Arcane Arrows).
- **`ShieldPerks`** covers Shield Wall knockback and durability, plus Mana Shield and Arcane Aegis.
- **`LivingEntityBlockMixin`** widens the shield angle for Bulwark.
- **Magic perks** (Scroll Saver, Druid's Grove, Wellspring) extend `IronsPerks` and `ArsPerks`. Wellspring also gets a regen term in `ConditionalStats`.
- **Earthshaker and Reaper's Due** extend `WeaponPerks`.
- **`Mana.spend`** takes mana from whichever magic mod has enough.
- **`Homing`** holds the pure steering math, which is unit-tested.

**Tech Stack:** Java 17 javac in Docker against SRG names. Forge 47.4.23 events and mixins. Python generator + pytest. Pufferfish 0.19.1.

**Spec:** `docs/superpowers/specs/2026-10-03-skills-design.md`. The relevant parts are "Homing arrows", "Quick casting ... chance an Iron's scroll isn't used up", Mana Shield ("blocking raises a mana barrier that works like a shield and spends mana per hit; Arcane Aegis makes it reflect damage"), and Multishot (rev 4).

## Global Constraints

- **No duplication.** Multishot clones can't be picked up. Retriever removes the projectile when it returns the item. Scroll Saver refunds only a scroll that was actually consumed.
- **Mob targets only.** Homing only curves toward hostile mobs (`Enemy`), and Reaper's Due only hits hostile mobs.
- **Mana Shield** needs no shield item in either hand. You must be crouching and facing the attacker, and it only blocks while you can pay the mana.
- **Carried rules:** perk ids live in `Perks.CAPS`, node ids keep `<slug>_<k>`, Pufferfish stays pinned at 0.19.1, and Iron's/Ars classes are touched only behind `ModList` guards.
- **Shipping:** after each build, update the sha512 and run `packwiz refresh`. Boot the test server with `PACK_REF=<pushed sha>`.

## Deferred (Ruling)

Artificer (Ars: cheaper glyph crafting, stronger summons) depends on Ars internals: the scribes table and summon stats. It waits for the tuning phase.

## Review Focus

1. **Multishot recursion.** Clones fire the same join event. A marker set must stop clones from making clones, and clones never return ammo.
2. **Homing** never steers into players or pets. It stops when the arrow lands, its target dies, or after 3 seconds.
3. **Mana Shield** must not block self-damage, falls or fire. The hit must come from a living attacker in front. It can't make you invulnerable when you have no mana.
4. **Bulwark's ModifyConstant** changes only the blocking-angle comparison (the second `dconst_0` in `isDamageSourceBlocked`), and only for players with the perk.
5. **Retriever** never duplicates. It skips tridents with Loyalty (they already return) and anything whose pickup isn't allowed.

---

### Task 1: Homing math

**Files:**
- Create: `extras/fotfskills/src/fotfskills/perk/Homing.java`, `extras/fotfskills/test/fotfskills/perk/HomingTest.java`

**Interfaces:**
- Produces: `Homing.steer(double[] velocity, double[] toTarget, double turn) -> double[]`. It turns the velocity toward the target direction by up to `turn` (0..1 blend of unit vectors) and keeps the original speed.

- [ ] **Step 1: Failing test**

```java
package fotfskills.perk;

/** Homing arrows keep their speed and turn toward the target. Run: sh test.sh */
public final class HomingTest {
    public static void main(String[] args) {
        double[] v = Homing.steer(new double[] {2, 0, 0}, new double[] {0, 0, 5}, 0);
        check(close(v[0], 2) && close(v[2], 0), "turn 0 changes nothing");
        v = Homing.steer(new double[] {2, 0, 0}, new double[] {0, 0, 5}, 1);
        check(close(v[0], 0) && close(v[2], 2), "turn 1 points straight at the target at the same speed");
        v = Homing.steer(new double[] {2, 0, 0}, new double[] {0, 0, 5}, 0.5);
        check(close(Math.sqrt(v[0] * v[0] + v[2] * v[2]), 2) && v[0] > 0 && v[2] > 0, "half turn keeps speed");
        System.out.println("HomingTest ok");
    }

    private static boolean close(double a, double b) {
        return Math.abs(a - b) < 1e-9;
    }

    private static void check(boolean ok, String what) {
        if (!ok) { System.out.println("FAIL: " + what); System.exit(1); }
    }
}
```

- [ ] **Step 2: Run the test.**
  - Run: `bash extras/fotfskills/test.sh`
  - Expected: it fails with `cannot find symbol: class Homing`.

- [ ] **Step 3: Implement**

```java
package fotfskills.perk;

/** Turns a projectile's velocity toward a target direction, keeping its speed. */
public final class Homing {
    private Homing() {
    }

    public static double[] steer(double[] velocity, double[] toTarget, double turn) {
        double speed = length(velocity);
        double tl = length(toTarget);
        if (speed == 0 || tl == 0 || turn <= 0) {
            return velocity.clone();
        }
        double[] out = new double[3];
        for (int i = 0; i < 3; i++) {
            out[i] = velocity[i] / speed * (1 - turn) + toTarget[i] / tl * turn;
        }
        double ol = length(out);
        for (int i = 0; i < 3; i++) {
            out[i] = ol == 0 ? velocity[i] : out[i] / ol * speed;
        }
        return out;
    }

    private static double length(double[] v) {
        return Math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2]);
    }
}
```

- [ ] **Step 4: Run the test again.**
  - Run: `bash extras/fotfskills/test.sh`
  - Expected: `HomingTest ok`, plus the earlier tests.

- [ ] **Step 5: Commit** `Skills 3d: homing steering math`.

---

### Task 2: Hooks

**Files:**
- Create in `extras/fotfskills/src/fotfskills/perk/`: `RangePerks.java`, `ShieldPerks.java`
- Create: `extras/fotfskills/src/fotfskills/mixin/LivingEntityBlockMixin.java`
- Modify:
  - `Perks.java` (new ids)
  - `Mana.java` (spend)
  - `IronsMana.java` and `ArsMana.java` (spend)
  - `IronsPerks.java` (Scroll Saver, Druid's Grove)
  - `ArsPerks.java` (Druid's Grove, Wellspring)
  - `ConditionalStats.java` (Wellspring for Iron's)
  - `WeaponPerks.java` (Earthshaker, Reaper's Due)
  - `fotfskills.mixins.json`
  - `FotfSkills.java`

- [ ] **Step 1: Add the perk ids to `Perks.CAPS`**

```java
            Map.entry("homing", 0.95), Map.entry("seeker", 1.0), Map.entry("multishot", 0.95),
            Map.entry("arcane_arrows", 2.0), Map.entry("retriever", 0.95), Map.entry("shield_wall", 0.9),
            Map.entry("bulwark", 0.6), Map.entry("mana_shield", 5.0), Map.entry("arcane_aegis", 1.0),
            Map.entry("scroll_saver", 0.95), Map.entry("wellspring", 2.0), Map.entry("druids_grove", 0.9),
            Map.entry("earthshaker", 1.0), Map.entry("reapers_due", 1.0)
```

- [ ] **Step 2: Add `Mana.spend` and its bridges.**

In `Mana`, add a second bridge list and `spend`:

```java
    private static final List<java.util.function.BiPredicate<ServerPlayer, Double>> SPENDERS = new ArrayList<>();

    public static void registerSpender(java.util.function.BiPredicate<ServerPlayer, Double> spender) {
        SPENDERS.add(spender);
    }

    /** Takes amount from the first magic mod that has that much; false if none does. */
    public static boolean spend(ServerPlayer player, double amount) {
        for (var spender : SPENDERS) {
            if (spender.test(player, amount)) {
                return true;
            }
        }
        return false;
    }
```

Add this to `IronsMana`:

```java
    public static boolean spend(ServerPlayer player, double amount) {
        MagicData data = MagicData.getPlayerMagicData(player);
        if (data.getMana() < amount) {
            return false;
        }
        data.setMana((float) (data.getMana() - amount));
        return true;
    }
```

Add this to `ArsMana`:

```java
    public static boolean spend(ServerPlayer player, double amount) {
        return CapabilityRegistry.getMana(player).map(mana -> {
            if (mana.getCurrentMana() < amount) {
                return false;
            }
            mana.removeMana(amount);
            return true;
        }).orElse(false);
    }
```

In `FotfSkills`, register `Mana.registerSpender(IronsMana::spend)` next to `Mana.register(IronsMana::add)`. Do the same for Ars.

- [ ] **Step 3: `RangePerks`**

```java
package fotfskills.perk;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Set;
import java.util.WeakHashMap;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.monster.Enemy;
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.world.entity.projectile.Arrow;
import net.minecraft.world.entity.projectile.Projectile;
import net.minecraft.world.entity.projectile.ThrownTrident;
import net.minecraft.world.item.enchantment.EnchantmentHelper;
import net.minecraft.world.item.enchantment.Enchantments;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.EntityJoinLevelEvent;
import net.minecraftforge.event.entity.ProjectileImpactEvent;
import net.minecraftforge.event.entity.living.LivingHurtEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.items.ItemHandlerHelper;

/**
 * Arrows: Homing Arrows and Seeker (curve toward the nearest hostile mob; Seeker triples the chance and makes them
 * crits), Multishot (two extra un-pickable arrows), Arcane Arrows (a full-draw arrow spends 5 mana for bonus damage).
 * Thrown weapons: Retriever (may come straight back to your inventory on impact).
 */
public final class RangePerks {
    private record Homer(AbstractArrow arrow, long until) {
    }

    private final List<Homer> homers = new ArrayList<>();
    private final Set<Projectile> clones = Collections.newSetFromMap(new WeakHashMap<>());
    private final Set<Projectile> arcane = Collections.newSetFromMap(new WeakHashMap<>());

    @SubscribeEvent
    public void onJoin(EntityJoinLevelEvent event) {
        if (event.loadedFromDisk() || event.getLevel().f_46443_ || !(event.getEntity() instanceof AbstractArrow arrow)
                || !(arrow.m_19749_() instanceof ServerPlayer player) || arrow.f_19797_ > 0 || clones.contains(arrow)
                || Projectiles.kind(arrow) != Projectiles.Kind.ARROW) {
            return;
        }
        long now = CombatState.now(player);
        double seeker = Perks.get(player, "seeker");
        if (Perks.random() < Perks.get(player, "homing") * (1 + 2 * seeker)) {
            homers.add(new Homer(arrow, now + 60));
        }
        if (seeker > 0) {
            arrow.m_36762_(true);
        }
        if (arrow.m_36792_() && Perks.get(player, "arcane_arrows") > 0 && Mana.spend(player, 5)) {
            arcane.add(arrow);
        }
        if (Perks.roll(player, "multishot") && event.getLevel() instanceof ServerLevel level) {
            for (double angle : new double[] {-0.17, 0.17}) {
                Arrow extra = new Arrow(level, player);
                Vec3 v = arrow.m_20184_();
                double cos = Math.cos(angle), sin = Math.sin(angle);
                extra.m_20256_(new Vec3(v.f_82479_ * cos - v.f_82481_ * sin, v.f_82480_, v.f_82479_ * sin + v.f_82481_ * cos));
                extra.m_6034_(arrow.m_20185_(), arrow.m_20186_(), arrow.m_20189_());
                extra.m_36781_(arrow.m_36789_());
                extra.m_36762_(arrow.m_36792_());
                extra.f_36705_ = AbstractArrow.Pickup.CREATIVE_ONLY;
                clones.add(extra);
                level.m_7967_(extra);
            }
        }
    }

    @SubscribeEvent
    public void onServerTick(TickEvent.ServerTickEvent event) {
        if (event.phase != TickEvent.Phase.END || homers.isEmpty()) {
            return;
        }
        homers.removeIf(h -> {
            AbstractArrow arrow = h.arrow;
            if (arrow.m_213877_() || arrow.m_20096_() || arrow.m_20184_().m_82556_() < 0.04
                    || arrow.m_9236_().m_46467_() > h.until) {
                return true;
            }
            LivingEntity target = null;
            double best = Double.MAX_VALUE;
            Vec3 pos = arrow.m_20182_();
            for (LivingEntity mob : arrow.m_9236_().m_45976_(LivingEntity.class, arrow.m_20191_().m_82400_(12))) {
                Vec3 to = mob.m_20182_().m_82520_(0, mob.m_20206_() / 2, 0).m_82546_(pos);
                if (mob instanceof Enemy && mob.m_6084_() && to.m_82526_(arrow.m_20184_()) > 0 && to.m_82556_() < best) {
                    best = to.m_82556_();
                    target = mob;
                }
            }
            if (target != null) {
                Vec3 to = target.m_20182_().m_82520_(0, target.m_20206_() / 2, 0).m_82546_(pos);
                Vec3 v = arrow.m_20184_();
                double[] s = Homing.steer(new double[] {v.f_82479_, v.f_82480_, v.f_82481_}, new double[] {to.f_82479_, to.f_82480_, to.f_82481_}, 0.25);
                arrow.m_20256_(new Vec3(s[0], s[1], s[2]));
            }
            return false;
        });
    }

    @SubscribeEvent
    public void onHurt(LivingHurtEvent event) {
        if (event.getSource().m_7640_() instanceof Projectile projectile && arcane.remove(projectile)
                && event.getSource().m_7639_() instanceof ServerPlayer player) {
            event.setAmount((float) (event.getAmount() * (1 + Perks.get(player, "arcane_arrows"))));
        }
    }

    /** Retriever: a thrown weapon that hits something may jump straight back to your inventory. */
    @SubscribeEvent
    public void onImpact(ProjectileImpactEvent event) {
        if (!(event.getProjectile() instanceof AbstractArrow thrown) || !(thrown.m_19749_() instanceof ServerPlayer player)
                || thrown.f_36705_ != AbstractArrow.Pickup.ALLOWED || Projectiles.kind(thrown) != Projectiles.Kind.THROWN
                || !(event.getRayTraceResult() instanceof EntityHitResult)) {
            return;
        }
        if (thrown instanceof ThrownTrident && EnchantmentHelper.m_44843_(Enchantments.f_44955_, Projectiles.item(thrown)) > 0) {
            return;                                   // Loyalty already brings it back
        }
        if (Perks.roll(player, "retriever")) {
            ItemHandlerHelper.giveItemToPlayer(player, Projectiles.item(thrown).m_41777_());
            thrown.f_36705_ = AbstractArrow.Pickup.CREATIVE_ONLY;
            thrown.m_146870_();
        }
    }
}
```

Verify these SRG names with javap:
- `m_6034_` is Entity.setPos.
- `m_20206_` is getBbHeight.
- `f_44955_` is Enchantments.LOYALTY.

Retriever removes the trident on hit, so the hit still deals its damage. The impact runs before damage, and removal takes effect at the end of the tick. Check this in the bytecode of `AbstractArrow.onHitEntity`. If removal happens too early, give the item back the next tick instead and log a Ruling.

- [ ] **Step 4: `ShieldPerks` and the Bulwark mixin**

```java
package fotfskills.perk;

import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ShieldItem;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.entity.living.LivingAttackEvent;
import net.minecraftforge.event.entity.living.LivingKnockBackEvent;
import net.minecraftforge.event.entity.living.ShieldBlockEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;

/**
 * Shield Wall (less knockback while blocking; a chance the shield takes no damage), Mana Shield (crouching with no
 * shield blocks a frontal hit from a living attacker by spending mana) and Arcane Aegis (reflects part of it as magic).
 */
public final class ShieldPerks {
    @SubscribeEvent
    public void onKnockback(LivingKnockBackEvent event) {
        if (event.getEntity() instanceof ServerPlayer player && player.m_21254_()) {
            event.setStrength((float) (event.getStrength() * (1 - Perks.get(player, "shield_wall"))));
        }
    }

    @SubscribeEvent
    public void onBlock(ShieldBlockEvent event) {
        if (event.getEntity() instanceof ServerPlayer player && Perks.roll(player, "shield_wall")) {
            event.setShieldTakesDamage(false);
        }
    }

    @SubscribeEvent
    public void onAttack(LivingAttackEvent event) {
        if (!(event.getEntity() instanceof ServerPlayer player) || !player.m_6047_()
                || player.m_21205_().m_41720_() instanceof ShieldItem || player.m_21206_().m_41720_() instanceof ShieldItem) {
            return;
        }
        double shield = Perks.get(player, "mana_shield");
        Entity attacker = event.getSource().m_7639_();
        if (shield <= 0 || !(attacker instanceof LivingEntity living) || attacker == player) {
            return;
        }
        Vec3 to = attacker.m_20182_().m_82546_(player.m_20182_()).m_82541_();
        if (to.m_82526_(player.m_20154_()) <= 0) {
            return;                                     // only hits from in front
        }
        double cost = event.getAmount() * 4 / (1 + shield);
        if (Mana.spend(player, cost)) {
            event.setCanceled(true);
            double aegis = Perks.get(player, "arcane_aegis");
            if (aegis > 0) {
                living.m_6469_(player.m_269291_().m_269425_(), (float) (event.getAmount() * aegis));
            }
        }
    }
}
```

```java
package fotfskills.mixin;

import fotfskills.perk.Perks;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.LivingEntity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.Constant;
import org.spongepowered.asm.mixin.injection.ModifyConstant;

/**
 * Bulwark: shields block a wider arc. isDamageSourceBlocked (m_21275_) blocks when the hit direction's dot product with
 * the view vector is below 0.0 (the second dconst_0, ordinal 1); Bulwark raises that threshold for the player.
 */
@Mixin(value = LivingEntity.class, remap = false)
public abstract class LivingEntityBlockMixin {
    @ModifyConstant(method = "m_21275_", remap = false, constant = @Constant(doubleValue = 0.0, ordinal = 1))
    private double fotfskills$widerBlock(double threshold) {
        if ((Object) this instanceof ServerPlayer player) {
            return threshold + Perks.get(player, "bulwark");
        }
        return threshold;
    }
}
```

Add `"LivingEntityBlockMixin"` to `mixins`. Bulwark also gets knockback resistance while blocking. In `ConditionalStats`, add `Modifiers.set(player, Attributes.f_22278_, "bulwark_kb", player.m_21254_() ? Perks.get(player, "bulwark") : 0, ADDITION)`. Verify `f_22278_` (KNOCKBACK_RESISTANCE) with javap.

- [ ] **Step 5: Magic and melee additions**
  - **`IronsPerks.onCast`** (caster branch):
    - **Druid's Grove:** in a forest biome (`#minecraft:is_forest`), `event.setManaCost((int) (event.getManaCost() * (1 - druids_grove)))`. Do this before the free-spell roll.
    - **Scroll Saver:** when `event.getCastSource() == CastSource.SCROLL` and `Perks.roll(caster, "scroll_saver")`, record the held scroll: whichever hand holds a `Scroll` item, its stack copy and its count. Record it in a static pending list, and process that list in a server tick handler in `IronsPerks`. On the next tick, if that hand's count dropped by one, or the hand is now empty, give the copy back with count 1.
  - **`ArsPerks`:**
    - `onCost`: also apply Druid's Grove, `currentCost = (int) (currentCost * (1 - druids_grove))`, when the caster is in a forest.
    - Add `onRegen(ManaRegenCalcEvent)`: if the entity is a ServerPlayer out of combat (`now - lastCombat > 200`), call `setRegen(getRegen() * (1 + wellspring))`.
  - **`ConditionalStats`:** add Wellspring to the Iron's regen value, `+ (now - state.lastCombat > 200 ? Perks.get(player, "wellspring") : 0)`.
  - **`WeaponPerks`:**
    - **Earthshaker:** in `onCrit`, if the weapon is blunt and the player has `earthshaker > 0`, every `Enemy` within 3 blocks of the target gets Slowness IV for 30 ticks.
    - **Reaper's Due:** in `onHurt`, on a primary scythe swing with `reapers_due > 0`, hit every `Enemy` within 3 blocks in front of the player at full damage. "In front" means the dot product with the look vector is above 0. Use the existing `splashing` guard. Reuse a variant of `splash` that takes a radius, a front-only flag and a damage value.

- [ ] **Step 6: Register and build**
  - Register `RangePerks` and `ShieldPerks` in `FotfSkills`.
  - Run: `bash extras/fotfskills/test.sh && bash extras/fotfskills/build.sh`
  - Expected: all tests print `ok`, and the build prints `Built`.

- [ ] **Step 7: Commit** `Skills 3d: range, shield and magic special perks`.

---

### Task 3: Wire the nodes

- [ ] **Step 1: Failing test** (append to `tools/skills/test_make_skill_trees.py`)

```python
def test_range_shield_magic_specials_are_wired():
    expect = {('range', 'homing_arrows_1'): ('homing', 0.05), ('range', 'seeker_1'): ('seeker', 1),
              ('range', 'multishot_1'): ('multishot', 0.1), ('range', 'arcane_arrows_1'): ('arcane_arrows', 0.15),
              ('range', 'retriever_1'): ('retriever', 0.25), ('defense', 'shield_wall_1'): ('shield_wall', 0.15),
              ('defense', 'bulwark_1'): ('bulwark', 0.1), ('magic', 'mana_shield_1'): ('mana_shield', 1),
              ('magic', 'arcane_aegis_1'): ('arcane_aegis', 0.1), ('magic', 'scroll_saver_1'): ('scroll_saver', 0.1),
              ('magic', 'wellspring_1'): ('wellspring', 1), ('forage', 'druids_grove_1'): ('druids_grove', 0.05),
              ('mining', 'earthshaker_1'): ('earthshaker', 1), ('farm', 'reapers_due_1'): ('reapers_due', 1)}
    for (tree_id, sid), (perk, value) in expect.items():
        defs = g.build_category(tree(tree_id), TIERS, XP, PERKS)['definitions.json']
        assert {'type': 'fotfskills:perk', 'data': {'perk': perk, 'value': value}} in defs[sid]['rewards'], sid
```

- [ ] **Step 2: Run** pytest. Expected: FAIL.

- [ ] **Step 3: Add the entries to `perks.json`.** Each node gets one perk reward (`P(id, v)`) with the values in the test above.

- [ ] **Step 4: Run.** Expected: all passed (32). Regenerate the config.

- [ ] **Step 5: Commit** `Skills 3d: range, shield and magic specials wired`.

---

### Task 4: Pack and boot

- [ ] **Step 1: Ship.** Update the sha512, run `packwiz refresh`, commit, push, and reboot the test server.
- [ ] **Step 2: Check the boot log.** Confirm that the config loaded and there are no fotfskills or mixin errors.
- [ ] **Step 3: Playtest rows to add:**
  - Homing arrows curve toward zombies.
  - Multishot fires 3 arrows and the extra 2 can't be picked up.
  - Mana Shield: crouch with an empty offhand and get hit from the front; mana drops and you take no damage.
  - Bulwark: a hit from the side gets blocked.
  - Scroll Saver: a scroll sometimes stays.
