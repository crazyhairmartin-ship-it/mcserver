# Skills Phase 3a: Weapon Types and Conditional Combat/Stat Perks Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship the weapon-type item tags and make the weapon and conditional nodes work:
- Weapon damage by type (pickaxes and blunt, axes, scythes, polearms, two-handers, thrown).
- Attack speed for light weapons and swords.
- Armour pierce and Crusher.
- Momentum, Flurry, Cleave, Lifeline, Grim Harvest and Berserker.
- Hunter's Mark, Shield Bash, Counter, Shield Thorns and Second Wind.
- Spellblade, Battlemage Plate and Spellbound Steel.
- Projectile speed and Spring Step.
- Situational stats: forest, combat, after a shot, after mining, saturation, grass, water/rain, armour pieces, gems, staff, full hunger, after a meal.
- Sea's Blessing, plus two static attribute nodes (Battlemage, Riptide Runner).

**Architecture:**
- **Weapon tags:** a Python generator turns `docs/superpowers/specs/2026-10-03-weapons.csv` into item tags `fotfskills:<type>`. They ship as a datapack inside the add-on jar (`res/data/fotfskills/tags/items/`), and `Weapons.is(stack, type)` reads them.
- **Pure logic, unit-tested:** `ArmorPierce`, `Streak` and `Cooldown`.
- **`CombatState`:** keeps per-player timestamps (last combat, shot, block, cast, stone mined, meal) and marks.
- **`WeaponPerks`:** event hooks for hits, deaths, blocks, projectiles and jumps.
- **`ConditionalStats`:** every 10 ticks, sets transient attribute modifiers from the player's situation and applies Earthbound healing and Sea's Blessing effects.
- **`Mana`:** gives mana to Iron's and Ars through bridges that are registered only when each mod is loaded.

**Tech Stack:** Python 3.12 + pytest. Java 17 javac in Docker against SRG names (`extras/fotfskills/build.sh`, `test.sh`). Forge 47.4.23 events. Pufferfish 0.19.1 (`fotfskills:perk` rewards from phase 2b).

**Spec:** `docs/superpowers/specs/2026-10-03-skills-design.md`. Relevant parts: "Unique and conditional", "Weapon types" (rev 4), the damage-tuning note, and `2026-10-03-weapons.csv`.

## Global Constraints

- Weapon types: sword, light, two_handed, polearm, axe, blunt, scythe, thrown, bow, crossbow (the firearms count as crossbows), magic. The add-on ships them as item tags `fotfskills:<type>`.
- Early damage nodes use flat bonuses (+0.3 per rank). Percent bonuses are for big-weapon branches (spec damage note).
- Bonuses are opt-in power only. No perk may damage players or tamed pets of the attacker (Cleave splash skips players and owned animals).
- Perk ids must be listed in `Perks.CAPS`. Node ids keep the `<slug>_<k>` scheme. Pufferfish stays pinned at 0.19.1.
- Client-only code stays out of the common path. Only `LivingJumpEvent` reads perks on the client, via the 2b sync.
- After each add-on build, update the sha512 in `mods/fotfskills.pw.toml` and run `packwiz refresh`. Boot the test server with `PACK_REF=<pushed sha>`.

## Review Focus

1. **Cleave recursion and friendly fire.** The splash hurts nearby mobs through `hurt()`, which re-enters LivingHurtEvent. A guard must stop chains, and splash never hits players or the attacker's tamed animals.
2. **Second Wind and totems.** It saves you only off cooldown (5 min), leaves 1 health, and never stacks with or eats a Totem of Undying.
3. **Attribute modifiers.** Fixed UUIDs, transient, removed when the condition ends and on logout. Max-health removal must not kill.
4. **Mod absence.** Iron's attributes are looked up by id and skipped when missing. Mana bridges load only with their mod.
5. **Projectile speed** applies once per projectile (not again after a portal or chunk reload) and only to projectiles a player fired.

---

### Task 1: Weapon type tags

**Files:**
- Create: `tools/skills/make_weapon_tags.py`, `tools/skills/test_make_weapon_tags.py`
- Create (generated): `extras/fotfskills/res/data/fotfskills/tags/items/{sword,light,two_handed,polearm,axe,blunt,scythe,thrown,bow,crossbow,magic}.json`
- Create: `extras/fotfskills/src/fotfskills/perk/Weapons.java`

**Interfaces:**
- Produces:
  - `make_weapon_tags.build(rows) -> {type: tag_json}`.
  - `Weapons.is(ItemStack, String type) -> boolean`. `type` is one of the 11 tags or `"pickaxe"` (`#minecraft:pickaxes`).

- [ ] **Step 1: Write the failing test** (`tools/skills/test_make_weapon_tags.py`)

```python
import csv
from pathlib import Path

import make_weapon_tags as w

ROWS = list(csv.DictReader((Path(__file__).parents[2] / 'docs/superpowers/specs/2026-10-03-weapons.csv').open(encoding='utf-8')))


def test_every_type_gets_a_tag_and_tool_is_not_one():
    tags = w.build(ROWS)
    assert set(tags) == set(w.TYPES)
    assert 'tool' not in tags
    for t, tag in tags.items():
        assert tag['replace'] is False and tag['values'], t


def test_items_are_optional_and_unique_and_vanilla_tags_included():
    tags = w.build(ROWS)
    sword = tags['sword']['values']
    ids = [v['id'] for v in sword if isinstance(v, dict)]
    assert len(ids) == len(set(ids))
    assert all(v['required'] is False for v in sword if isinstance(v, dict))
    assert '#minecraft:swords' in sword and '#minecraft:axes' in tags['axe']['values']


def test_multi_type_rows_land_in_each_type_and_firearms_are_crossbows():
    tags = w.build(ROWS)
    def has(t, item):
        return any(isinstance(v, dict) and v['id'] == item for v in tags[t]['values'])
    halberd = next(r['item'] for r in ROWS if r['weapon types'] == 'polearm axe two_handed')
    assert has('polearm', halberd) and has('axe', halberd) and has('two_handed', halberd)
    assert has('crossbow', 'wildernature:blunderbuss')
```

- [ ] **Step 2: Run it to verify it fails.**
  - Run: `python -m pytest -q -p no:cacheprovider tools/skills`
  - Expected: `ModuleNotFoundError: No module named 'make_weapon_tags'`.

- [ ] **Step 3: Implement** `tools/skills/make_weapon_tags.py`:

```python
"""Turns docs/superpowers/specs/2026-10-03-weapons.csv into fotfskills:<type> item tags shipped in the add-on jar.

Run: python tools/skills/make_weapon_tags.py   (writes extras/fotfskills/res/data/fotfskills/tags/items/<type>.json)
Entries are optional ("required": false) so a removed mod never breaks tag loading. 'tool' rows (pickaxes, shovels)
are not a weapon type; the add-on reads #minecraft:pickaxes for Miner's Might.
"""
import csv
import json
from pathlib import Path

HERE = Path(__file__).parent
PACK = HERE.parent.parent
CSV = PACK / 'docs' / 'superpowers' / 'specs' / '2026-10-03-weapons.csv'
OUT = PACK / 'extras' / 'fotfskills' / 'res' / 'data' / 'fotfskills' / 'tags' / 'items'
TYPES = ['sword', 'light', 'two_handed', 'polearm', 'axe', 'blunt', 'scythe', 'thrown', 'bow', 'crossbow', 'magic']
VANILLA = {'sword': ['#minecraft:swords'], 'axe': ['#minecraft:axes'], 'polearm': ['minecraft:trident'],
           'thrown': ['minecraft:trident'], 'bow': ['minecraft:bow'], 'crossbow': ['minecraft:crossbow']}


def build(rows):
    items = {t: [] for t in TYPES}
    for row in rows:
        for t in row['weapon types'].split():
            if t in items and row['item'] not in items[t]:
                items[t].append(row['item'])
    tags = {}
    for t in TYPES:
        values = list(VANILLA.get(t, []))
        values += [{'id': i, 'required': False} for i in sorted(items[t]) if i not in VANILLA.get(t, [])]
        tags[t] = {'replace': False, 'values': values}
    return tags


def main():
    rows = list(csv.DictReader(CSV.open(encoding='utf-8')))
    OUT.mkdir(parents=True, exist_ok=True)
    for t, tag in build(rows).items():
        (OUT / f'{t}.json').write_text(json.dumps(tag, indent=2) + '\n', encoding='utf-8')
    print(f'wrote {len(TYPES)} weapon tags to {OUT}')


if __name__ == '__main__':
    main()
```

`extras/fotfskills/src/fotfskills/perk/Weapons.java`:

```java
package fotfskills.perk;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.tags.TagKey;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.registries.ForgeRegistries;

/** Weapon types from the fotfskills:<type> item tags (tools/skills/make_weapon_tags.py); "pickaxe" = #minecraft:pickaxes. */
public final class Weapons {
    private static final Map<String, TagKey<Item>> TAGS = new ConcurrentHashMap<>();

    private Weapons() {
    }

    public static boolean is(ItemStack stack, String type) {
        if (stack.m_41619_()) {
            return false;
        }
        TagKey<Item> tag = TAGS.computeIfAbsent(type, t -> TagKey.m_203882_(ForgeRegistries.Keys.ITEMS,
                t.equals("pickaxe") ? new ResourceLocation("minecraft", "pickaxes") : new ResourceLocation("fotfskills", t)));
        return stack.m_204117_(tag);
    }
}
```

- [ ] **Step 4: Run the tests.**
  - Run: `python tools/skills/make_weapon_tags.py && python -m pytest -q -p no:cacheprovider tools/skills`
  - Expected: `wrote 11 weapon tags`, all passed (28).

- [ ] **Step 5: Commit**

```bash
git add tools/skills extras/fotfskills
git commit -m "Skills 3a: weapon type item tags from the weapons CSV"
```

---

### Task 2: Pure combat logic

**Files:**
- Create: `extras/fotfskills/src/fotfskills/perk/{ArmorPierce,Streak,Cooldown}.java`
- Create: `extras/fotfskills/test/fotfskills/perk/CombatLogicTest.java`

**Interfaces:**
- Produces:
  - `ArmorPierce.multiplier(double armor, double toughness, double damage, double pierce) -> double`. This is the damage multiplier that makes armour count as if `pierce` of it were missing, using vanilla's armour formula.
  - `Streak(long window, int max)` with `.hit(long now) -> int` (the streak length after this hit, capped) and `.reset()`.
  - `Cooldown(long ticks)` with `.ready(long now)` and `.trigger(long now)`.

- [ ] **Step 1: Write the failing test** (`CombatLogicTest.java`):

```java
package fotfskills.perk;

/** Plain-java tests of the combat math. Run: sh test.sh */
public final class CombatLogicTest {
    public static void main(String[] args) {
        check(close(ArmorPierce.multiplier(0, 0, 10, 0.3), 1.0), "no armour, nothing to pierce");
        check(close(ArmorPierce.multiplier(20, 0, 10, 0), 1.0), "no pierce, no change");
        // 20 armour, 10 dmg, no toughness (t = 2): effective = max(20 - 10/2, 20*0.2) = 15 -> 15/25 = 0.6 -> 4 dmg.
        // Half the armour pierced: max(10 - 5, 2) = 5 -> 0.2 -> 8 dmg; multiplier 8/4 = 2.0
        check(close(ArmorPierce.multiplier(20, 0, 10, 0.5), 2.0), "half armour pierced doubles the damage taken");

        Streak streak = new Streak(60, 3);
        check(streak.hit(0) == 1 && streak.hit(20) == 2 && streak.hit(40) == 3, "hits in a row build");
        check(streak.hit(50) == 3, "capped at 3");
        check(streak.hit(200) == 1, "a long gap restarts");

        Cooldown cd = new Cooldown(6000);
        check(cd.ready(0), "ready at first");
        cd.trigger(100);
        check(!cd.ready(5000) && cd.ready(6100), "ready again after 6000 ticks");
        System.out.println("CombatLogicTest ok");
    }

    private static boolean close(double a, double b) {
        return Math.abs(a - b) < 1e-6;
    }

    private static void check(boolean ok, String what) {
        if (!ok) { System.out.println("FAIL: " + what); System.exit(1); }
    }
}
```

- [ ] **Step 2: Run it to verify it fails.**
  - Run: `bash extras/fotfskills/test.sh`
  - Expected: javac `cannot find symbol: class ArmorPierce` (and `Streak`, `Cooldown`).

- [ ] **Step 3: Implement**

```java
package fotfskills.perk;

/** Damage multiplier for ignoring part of the target's armour (vanilla CombatRules.getDamageAfterAbsorb). */
public final class ArmorPierce {
    private ArmorPierce() {
    }

    public static double multiplier(double armor, double toughness, double damage, double pierce) {
        if (armor <= 0 || pierce <= 0 || damage <= 0) {
            return 1;
        }
        double full = afterArmor(armor, toughness, damage);
        return full <= 0 ? 1 : afterArmor(armor * (1 - Math.min(pierce, 1)), toughness, damage) / full;
    }

    private static double afterArmor(double armor, double toughness, double damage) {
        double t = 2 + toughness / 4;
        double effective = Math.max(Math.min(armor - damage / t, 20), armor * 0.2);
        return damage * (1 - Math.min(effective, 20) / 25);
    }
}
```

```java
package fotfskills.perk;

/** Consecutive actions within a window of ticks, capped (Momentum stacks, Flurry's every-5th-hit count). */
public final class Streak {
    private final long window;
    private final int max;
    private long last = Long.MIN_VALUE / 2;
    private int count;

    public Streak(long window, int max) {
        this.window = window;
        this.max = max;
    }

    public int hit(long now) {
        count = now - last <= window ? Math.min(count + 1, max) : 1;
        last = now;
        return count;
    }

    public void reset() {
        count = 0;
    }
}
```

```java
package fotfskills.perk;

/** A per-player cooldown in ticks (Second Wind). */
public final class Cooldown {
    private final long ticks;
    private long readyAt;

    public Cooldown(long ticks) {
        this.ticks = ticks;
    }

    public boolean ready(long now) {
        return now >= readyAt;
    }

    public void trigger(long now) {
        readyAt = now + ticks;
    }
}
```

- [ ] **Step 4: Run.**
  - Run: `bash extras/fotfskills/test.sh`
  - Expected: `CombatLogicTest ok` plus the 2b tests.

- [ ] **Step 5: Commit**

```bash
git add extras/fotfskills
git commit -m "Skills 3a: armour pierce, streak and cooldown logic"
```

---

### Task 3: Weapon and combat perk hooks

**Files:**
- Create: `extras/fotfskills/src/fotfskills/perk/{CombatState,WeaponPerks,Mana}.java`, `extras/fotfskills/src/fotfskills/perk/{IronsMana,ArsMana}.java`
- Modify: `Perks.java` (new ids), `IronsPerks.java` and `mixin/ArsSpellResolverMixin.java` (mark casts), `FotfSkills.java`

**Interfaces:**
- Consumes: `Weapons.is`, `ArmorPierce`, `Streak`, `Cooldown`, `Perks.get/roll`.
- Produces:
  - `CombatState.of(ServerPlayer)`. Fields: `lastCombat`, `lastShot`, `lastBlock`, `counterReady`, `lastCast`, `lastStoneMined`, `lastMeal` (game ticks), `momentum`, `flurry` (Streak), `secondWind` (Cooldown), `markedTarget` (UUID), `markedUntil`.
  - `CombatState.now(player)`.
  - `Mana.add(ServerPlayer, double)`.

- [ ] **Step 1: Add the perk ids to `Perks.CAPS`.** Append these entries:

```java
            Map.entry("dmg_pickaxe_blunt", 10.0), Map.entry("dmg_axe", 10.0), Map.entry("dmg_scythe", 10.0),
            Map.entry("dmg_polearm", 10.0), Map.entry("pct_two_handed", 2.0), Map.entry("pct_thrown", 2.0),
            Map.entry("pct_thrown_axe", 2.0), Map.entry("armor_pierce_axe", 0.9), Map.entry("crush_armor", 5.0),
            Map.entry("momentum", 1.0), Map.entry("flurry", 1.0), Map.entry("cleave", 1.0), Map.entry("lifeline", 4.0),
            Map.entry("grim_harvest", 6.0), Map.entry("berserker", 20.0), Map.entry("hunters_mark", 1.0),
            Map.entry("shield_bash", 2.0), Map.entry("counter", 2.0), Map.entry("shield_thorns", 0.95),
            Map.entry("second_wind", 1.0), Map.entry("spellbound_steel", 1.0), Map.entry("spellblade_mana", 10.0),
            Map.entry("battlemage_mana", 20.0), Map.entry("projectile_speed", 1.0), Map.entry("thrown_speed", 1.0),
            Map.entry("jump_boost", 0.5), Map.entry("forest_speed", 1.0), Map.entry("forest_toughness", 10.0),
            Map.entry("combat_speed", 1.0), Map.entry("skirmish_speed", 1.0), Map.entry("stonehide", 10.0),
            Map.entry("iron_stomach", 20.0), Map.entry("earthbound", 5.0), Map.entry("tide_spell", 1.0),
            Map.entry("warded_spell", 1.0), Map.entry("gem_spell", 1.0), Map.entry("staff_spell", 1.0),
            Map.entry("staff_cooldown", 1.0), Map.entry("feast_spell", 1.0), Map.entry("brain_regen", 2.0),
            Map.entry("duelist_speed", 1.0), Map.entry("light_speed", 1.0), Map.entry("seas_blessing", 1.0)
```

`Map.ofEntries` takes varargs, so this works as long as the list stays one call.

- [ ] **Step 2: Write `CombatState`, `Mana` and the bridges**

```java
package fotfskills.perk;

import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import net.minecraft.server.level.ServerPlayer;

/** Per-player combat timestamps (game ticks) and streaks. Cleared on logout (WeaponPerks). */
public final class CombatState {
    private static final Map<UUID, CombatState> STATES = new ConcurrentHashMap<>();
    public long lastCombat = -100000, lastShot = -100000, lastBlock = -100000, lastCast = -100000;
    public long lastStoneMined = -100000, lastMeal = -100000;
    public boolean counterReady;
    public final Streak momentum = new Streak(60, 3);
    public final Streak flurry = new Streak(40, 5);
    public final Cooldown secondWind = new Cooldown(6000);
    public UUID markedTarget;
    public long markedUntil;

    public static CombatState of(ServerPlayer player) {
        return STATES.computeIfAbsent(player.m_20148_(), id -> new CombatState());
    }

    public static long now(ServerPlayer player) {
        return player.m_9236_().m_46467_();
    }

    public static void forget(UUID player) {
        STATES.remove(player);
    }
}
```

```java
package fotfskills.perk;

import java.util.ArrayList;
import java.util.List;
import java.util.function.BiConsumer;
import net.minecraft.server.level.ServerPlayer;

/** Gives mana in whichever magic mods are installed (bridges registered by FotfSkills when the mod is loaded). */
public final class Mana {
    private static final List<BiConsumer<ServerPlayer, Double>> BRIDGES = new ArrayList<>();

    private Mana() {
    }

    public static void register(BiConsumer<ServerPlayer, Double> bridge) {
        BRIDGES.add(bridge);
    }

    public static void add(ServerPlayer player, double amount) {
        if (amount > 0) {
            BRIDGES.forEach(bridge -> bridge.accept(player, amount));
        }
    }
}
```

```java
package fotfskills.perk;

import io.redspace.ironsspellbooks.api.magic.MagicData;
import io.redspace.ironsspellbooks.api.registry.AttributeRegistry;
import net.minecraft.server.level.ServerPlayer;

/** Iron's Spells mana, clamped to the player's max mana. Loaded only if irons_spellbooks is present. */
public final class IronsMana {
    private IronsMana() {
    }

    public static void add(ServerPlayer player, double amount) {
        MagicData data = MagicData.getPlayerMagicData(player);
        double max = player.m_21133_(AttributeRegistry.MAX_MANA.get());
        data.setMana((float) Math.min(max, data.getMana() + amount));
    }
}
```

```java
package fotfskills.perk;

import com.hollingsworth.arsnouveau.setup.registry.CapabilityRegistry;
import net.minecraft.server.level.ServerPlayer;

/** Ars Nouveau mana. Loaded only if ars_nouveau is present. */
public final class ArsMana {
    private ArsMana() {
    }

    public static void add(ServerPlayer player, double amount) {
        CapabilityRegistry.getMana(player).ifPresent(mana -> mana.addMana(amount));
    }
}
```

`m_21133_` is LivingEntity.getAttributeValue(Attribute); verify it with javap.

- [ ] **Step 3: Write `WeaponPerks`**

```java
package fotfskills.perk;

import fotfskills.mixin.AbstractArrowAccessor;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.tags.TagKey;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.OwnableEntity;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.world.entity.projectile.Projectile;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.EntityJoinLevelEvent;
import net.minecraftforge.event.entity.living.LivingDamageEvent;
import net.minecraftforge.event.entity.living.LivingDeathEvent;
import net.minecraftforge.event.entity.living.LivingEntityUseItemEvent;
import net.minecraftforge.event.entity.living.LivingEvent;
import net.minecraftforge.event.entity.living.LivingHurtEvent;
import net.minecraftforge.event.entity.living.ShieldBlockEvent;
import net.minecraftforge.event.entity.player.CriticalHitEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.registries.ForgeRegistries;

/** Weapon-type damage and the conditional combat perks (Attack, Defense, Range, plus cross-tree weapon nodes). */
public final class WeaponPerks {
    private static final TagKey<Item> ARROWS = TagKey.m_203882_(ForgeRegistries.Keys.ITEMS, new ResourceLocation("minecraft", "arrows"));
    private static final UUID CRUSH = UUID.nameUUIDFromBytes("fotfskills:crush".getBytes());
    /** Crushed targets: entity -> tick the armour debuff ends. */
    private final Map<LivingEntity, Long> crushed = new ConcurrentHashMap<>();
    /** Guards Cleave's splash so it never chains. */
    private boolean splashing;

    @SubscribeEvent(priority = EventPriority.LOW)
    public void onHurt(LivingHurtEvent event) {
        LivingEntity target = event.getEntity();
        Entity attacker = event.getSource().m_7639_();
        Entity direct = event.getSource().m_7640_();
        if (target instanceof ServerPlayer hurtPlayer && attacker instanceof LivingEntity && attacker != hurtPlayer) {
            CombatState.of(hurtPlayer).lastCombat = CombatState.now(hurtPlayer);
            Mana.add(hurtPlayer, Perks.get(hurtPlayer, "battlemage_mana"));
        }
        if (!(attacker instanceof ServerPlayer player) || attacker == target || splashing) {
            return;
        }
        CombatState state = CombatState.of(player);
        long now = CombatState.now(player);
        state.lastCombat = now;
        float amount = event.getAmount();
        if (direct == player) {
            ItemStack weapon = player.m_21205_();
            if (Weapons.is(weapon, "pickaxe") || Weapons.is(weapon, "blunt")) {
                amount += Perks.get(player, "dmg_pickaxe_blunt");
            }
            if (Weapons.is(weapon, "axe")) {
                amount += Perks.get(player, "dmg_axe");
                amount *= (float) ArmorPierce.multiplier(target.m_21230_(), target.m_21133_(Attributes.f_22285_), amount,
                        Perks.get(player, "armor_pierce_axe"));
            }
            if (Weapons.is(weapon, "scythe")) {
                amount += Perks.get(player, "dmg_scythe");
            }
            if (Weapons.is(weapon, "polearm")) {
                amount += Perks.get(player, "dmg_polearm");
            }
            double pct = 0;
            if (Weapons.is(weapon, "two_handed")) {
                pct += Perks.get(player, "pct_two_handed");
            }
            double momentum = Perks.get(player, "momentum");
            if (momentum > 0) {
                pct += momentum * (state.momentum.hit(now) - 1);
            }
            if (now - state.lastBlock <= 40) {
                pct += Perks.get(player, "shield_bash");
            }
            if (state.counterReady) {
                pct += Perks.get(player, "counter");
                state.counterReady = false;
            }
            if (now - state.lastCast <= 200 && Perks.get(player, "spellbound_steel") > 0) {
                pct += Perks.get(player, "spellbound_steel");
                state.lastCast = -100000;          // the next hit only
            }
            amount *= (float) (1 + pct);
            if ((Weapons.is(weapon, "light") || Weapons.is(weapon, "sword")) && Perks.get(player, "flurry") > 0
                    && state.flurry.hit(now) == 5) {
                amount *= 2;                        // Flurry: every 5th quick hit strikes twice
                state.flurry.reset();
            }
            if (Weapons.is(weapon, "blunt") && Perks.get(player, "crush_armor") > 0) {
                crush(target, Perks.get(player, "crush_armor"), now);
            }
            Mana.add(player, Perks.get(player, "spellblade_mana"));
            state.markedTarget = target.m_20148_();
            state.markedUntil = now + 200;
            event.setAmount(amount);
            double cleave = Perks.get(player, "cleave");
            if (cleave > 0 && Weapons.is(weapon, "two_handed")) {
                splash(player, target, amount * cleave);
            }
        } else if (direct instanceof Projectile projectile) {
            double pct = 0;
            if (thrown(projectile)) {
                pct += Perks.get(player, "pct_thrown");
                ItemStack item = projectile instanceof AbstractArrow arrow ? ((AbstractArrowAccessor) arrow).fotfskills$pickupItem() : ItemStack.f_41583_;
                if (Weapons.is(item, "axe")) {
                    pct += Perks.get(player, "pct_thrown_axe");
                }
            }
            if (target.m_20148_().equals(state.markedTarget) && now <= state.markedUntil) {
                pct += Perks.get(player, "hunters_mark");
            }
            event.setAmount((float) (amount * (1 + pct)));
        }
    }

    /** Second Wind: a hit that would kill leaves you on 1 health, once per 5 minutes (totems are left alone). */
    @SubscribeEvent(priority = EventPriority.LOWEST)
    public void onDamage(LivingDamageEvent event) {
        if (event.getEntity() instanceof ServerPlayer player && event.getAmount() >= player.m_21223_()
                && Perks.get(player, "second_wind") > 0 && !holdingTotem(player)) {
            CombatState state = CombatState.of(player);
            long now = CombatState.now(player);
            if (state.secondWind.ready(now)) {
                state.secondWind.trigger(now);
                event.setAmount(Math.max(0, player.m_21223_() - 1));
            }
        }
    }

    @SubscribeEvent
    public void onDeath(LivingDeathEvent event) {
        if (!(event.getSource().m_7639_() instanceof ServerPlayer player) || event.getSource().m_7640_() != player) {
            return;
        }
        ItemStack weapon = player.m_21205_();
        if (Weapons.is(weapon, "scythe")) {
            player.m_5634_((float) Perks.get(player, "grim_harvest"));
        }
        double berserk = Perks.get(player, "berserker");
        if (berserk > 0 && Weapons.is(weapon, "axe")) {
            player.m_7292_(new MobEffectInstance(MobEffects.f_19600_, (int) (berserk * 20), 0, false, true));
        }
    }

    @SubscribeEvent
    public void onCrit(CriticalHitEvent event) {
        if (event.getEntity() instanceof ServerPlayer player && (event.isVanillaCritical() || event.getDamageModifier() > 1)) {
            player.m_5634_((float) Perks.get(player, "lifeline"));
        }
    }

    @SubscribeEvent
    public void onBlock(ShieldBlockEvent event) {
        if (!(event.getEntity() instanceof ServerPlayer player)) {
            return;
        }
        CombatState state = CombatState.of(player);
        state.lastBlock = CombatState.now(player);
        state.counterReady = Perks.get(player, "counter") > 0;
        Entity attacker = event.getDamageSource().m_7639_();
        if (attacker instanceof LivingEntity living && attacker != player && Perks.roll(player, "shield_thorns")) {
            living.m_6469_(player.m_269291_().m_269075_(player), event.getBlockedDamage() * 0.3f);
        }
    }

    /** Projectiles a player fires: Eagle Eye (all) and Throwing Arm (thrown) speed; marks the shot for Skirmisher. */
    @SubscribeEvent
    public void onJoin(EntityJoinLevelEvent event) {
        if (event.loadedFromDisk() || event.getLevel().f_46443_ || !(event.getEntity() instanceof Projectile projectile)
                || !(projectile.m_19749_() instanceof ServerPlayer player) || projectile.f_19797_ > 0) {
            return;
        }
        CombatState.of(player).lastShot = CombatState.now(player);
        double speed = Perks.get(player, "projectile_speed") + (thrown(projectile) ? Perks.get(player, "thrown_speed") : 0);
        if (speed > 0) {
            projectile.m_20256_(projectile.m_20184_().m_82490_(1 + speed));
        }
    }

    /** Spring Step: jump higher. Runs on the client too (player movement is client-side); reads synced totals. */
    @SubscribeEvent
    public void onJump(LivingEvent.LivingJumpEvent event) {
        if (event.getEntity() instanceof Player player) {
            double boost = Perks.get(player, "jump_boost");
            if (boost > 0) {
                player.m_20256_(player.m_20184_().m_82520_(0, boost, 0));
            }
        }
    }

    /** Brain Food: finishing a meal starts the mana-regen window (ConditionalStats). */
    @SubscribeEvent
    public void onEat(LivingEntityUseItemEvent.Finish event) {
        if (event.getEntity() instanceof ServerPlayer player && event.getItem().m_41614_()) {
            CombatState.of(player).lastMeal = CombatState.now(player);
        }
    }

    @SubscribeEvent
    public void onServerTick(TickEvent.ServerTickEvent event) {
        if (event.phase != TickEvent.Phase.END || crushed.isEmpty()) {
            return;
        }
        crushed.entrySet().removeIf(entry -> {
            LivingEntity target = entry.getKey();
            if (target.m_213877_() || target.m_9236_().m_46467_() >= entry.getValue()) {
                AttributeInstance armor = target.m_21051_(Attributes.f_22284_);
                if (armor != null) {
                    armor.m_22120_(CRUSH);
                }
                return true;
            }
            return false;
        });
    }

    @SubscribeEvent
    public void onLogout(PlayerEvent.PlayerLoggedOutEvent event) {
        CombatState.forget(event.getEntity().m_20148_());
    }

    /** Thrown weapons: any player projectile except a normal arrow (tridents, javelins, tomahawks, knives). */
    private static boolean thrown(Projectile projectile) {
        if (projectile instanceof AbstractArrow arrow) {
            return !((AbstractArrowAccessor) arrow).fotfskills$pickupItem().m_204117_(ARROWS);
        }
        return true;
    }

    private static boolean holdingTotem(Player player) {
        ResourceLocation totem = new ResourceLocation("minecraft", "totem_of_undying");
        return totem.equals(ForgeRegistries.ITEMS.getKey(player.m_21205_().m_41720_()))
                || totem.equals(ForgeRegistries.ITEMS.getKey(player.m_21206_().m_41720_()));
    }

    /** Crusher: the target loses armour for 5 s, stacking with each hit up to 5 points. */
    private void crush(LivingEntity target, double perHit, long now) {
        AttributeInstance armor = target.m_21051_(Attributes.f_22284_);
        if (armor == null) {
            return;
        }
        AttributeModifier old = armor.m_22111_(CRUSH);
        double value = Math.max(-5, (old == null ? 0 : old.m_22218_()) - perHit);
        armor.m_22120_(CRUSH);
        armor.m_22118_(new AttributeModifier(CRUSH, "fotfskills crush", value, AttributeModifier.Operation.ADDITION));
        crushed.put(target, now + 100);
    }

    /** Cleave: part of a two-handed hit splashes to mobs around the target; never players or the attacker's pets. */
    private void splash(ServerPlayer player, LivingEntity target, float damage) {
        splashing = true;
        try {
            for (LivingEntity other : target.m_9236_().m_45976_(LivingEntity.class, target.m_20191_().m_82400_(2.5))) {
                if (other == target || other == player || other instanceof Player
                        || (other instanceof OwnableEntity pet && player.m_20148_().equals(pet.m_21805_()))) {
                    continue;
                }
                other.m_6469_(player.m_269291_().m_269075_(player), damage);
            }
        } finally {
            splashing = false;
        }
    }
}
```

Verify these with javap and correct any javac rejects in place:

| SRG name | Method or field |
|---|---|
| `m_21206_` | getOffhandItem |
| `f_19797_` | Entity.tickCount |
| `f_41583_` | ItemStack.EMPTY |
| `m_21805_` | OwnableEntity.getOwnerUUID |
| `m_21133_` | getAttributeValue |

In `IronsPerks.onCast` (any Iron's cast, before the free-spell roll), add:

```java
        if (event.getEntity() instanceof ServerPlayer caster) {
            CombatState.of(caster).lastCast = CombatState.now(caster);
        }
```

In `ArsSpellResolverMixin.fotfskills$magicXp`, inside the `ServerPlayer` branch, add `fotfskills.perk.CombatState.of(player).lastCast = fotfskills.perk.CombatState.now(player);`.

In `FotfSkills`, register `new WeaponPerks()` on the Forge bus. Inside the Iron's branch add `Mana.register(IronsMana::add);`, and inside the Ars branch add `Mana.register(ArsMana::add);`.

- [ ] **Step 4: Build and test**
  - Run: `bash extras/fotfskills/test.sh` (expect all `ok`), then `bash extras/fotfskills/build.sh` (expect `Built`).

- [ ] **Step 5: Commit**

```bash
git add extras/fotfskills
git commit -m "Skills 3a: weapon-type damage and conditional combat perks"
```

---

### Task 4: Situational stats

**Files:**
- Create: `extras/fotfskills/src/fotfskills/perk/ConditionalStats.java`
- Modify: `perk/BlockPerks.java` (Stonehide timestamp on stone/ore breaks), `FotfSkills.java`

**Interfaces:**
- Consumes: `CombatState` timestamps, `Weapons.is`, `Perks.get`.
- Produces: nothing for later tasks.

- [ ] **Step 1: Write `ConditionalStats`**

```java
package fotfskills.perk;

import java.util.HashSet;
import java.util.Set;
import java.util.UUID;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.tags.TagKey;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.ai.attributes.Attribute;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.biome.Biome;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.registries.ForgeRegistries;

/**
 * Stats that depend on the situation, refreshed every 10 ticks as transient attribute modifiers with fixed UUIDs:
 * Forest Stride / Bark Skin (forest biomes), Footwork (in combat), Skirmisher (after a shot), Stonehide (after
 * mining), Iron Stomach (saturation above half), Duelist / Light Weapons (weapon held), and Iron's spell power,
 * cooldowns and mana regen (Tidecaller, Warded Mind, Gem Focus, Staff Adept, Warrior's Feast, Brain Food).
 * Also Earthbound healing and Sea's Blessing effects.
 */
public final class ConditionalStats {
    private static final TagKey<Biome> FOREST = TagKey.m_203882_(ForgeRegistries.Keys.BIOMES, new ResourceLocation("minecraft", "is_forest"));
    private static final TagKey<Item> GEMS = TagKey.m_203882_(ForgeRegistries.Keys.ITEMS, new ResourceLocation("forge", "gems"));

    @SubscribeEvent
    public void onTick(TickEvent.PlayerTickEvent event) {
        if (event.phase != TickEvent.Phase.END || !(event.player instanceof ServerPlayer player) || player.f_19797_ % 10 != 0) {
            return;
        }
        CombatState state = CombatState.of(player);
        long now = CombatState.now(player);
        boolean forest = player.m_9236_().m_204166_(player.m_20183_()).m_203656_(FOREST);
        boolean inCombat = now - state.lastCombat <= 100;
        ItemStack held = player.m_21205_();

        double speed = (forest ? Perks.get(player, "forest_speed") : 0) + (inCombat ? Perks.get(player, "combat_speed") : 0)
                + (now - state.lastShot <= 40 ? Perks.get(player, "skirmish_speed") : 0);
        set(player, Attributes.f_22279_, "speed", speed, AttributeModifier.Operation.MULTIPLY_TOTAL);
        set(player, Attributes.f_22285_, "toughness", forest ? Perks.get(player, "forest_toughness") : 0, AttributeModifier.Operation.ADDITION);
        set(player, Attributes.f_22284_, "armor", now - state.lastStoneMined <= 600 ? Perks.get(player, "stonehide") : 0,
                AttributeModifier.Operation.ADDITION);
        set(player, Attributes.f_22276_, "health", player.m_36324_().m_38722_() > 10 ? Perks.get(player, "iron_stomach") : 0,
                AttributeModifier.Operation.ADDITION);
        double attackSpeed = (Weapons.is(held, "light") || Weapons.is(held, "sword") ? Perks.get(player, "duelist_speed") : 0)
                + (Weapons.is(held, "light") ? Perks.get(player, "light_speed") : 0);
        set(player, Attributes.f_22283_, "attack_speed", attackSpeed, AttributeModifier.Operation.MULTIPLY_TOTAL);

        boolean staff = Weapons.is(held, "magic");
        int armourPieces = 0;
        for (ItemStack piece : player.m_6168_()) {
            armourPieces += piece.m_41619_() ? 0 : 1;
        }
        Set<Item> gems = new HashSet<>();
        for (ItemStack stack : player.m_150109_().f_35974_) {
            if (stack.m_204117_(GEMS)) {
                gems.add(stack.m_41720_());
            }
        }
        double spell = (player.m_20070_() ? Perks.get(player, "tide_spell") : 0)
                + armourPieces * Perks.get(player, "warded_spell") + gems.size() * Perks.get(player, "gem_spell")
                + (staff ? Perks.get(player, "staff_spell") : 0)
                + (player.m_36324_().m_38702_() >= 20 ? Perks.get(player, "feast_spell") : 0);
        set(player, attribute("irons_spellbooks", "spell_power"), "spell", spell, AttributeModifier.Operation.MULTIPLY_BASE);
        set(player, attribute("irons_spellbooks", "cooldown_reduction"), "cooldown", staff ? Perks.get(player, "staff_cooldown") : 0,
                AttributeModifier.Operation.ADDITION);
        set(player, attribute("irons_spellbooks", "mana_regen"), "regen", now - state.lastMeal <= 1200 ? Perks.get(player, "brain_regen") : 0,
                AttributeModifier.Operation.MULTIPLY_BASE);

        if (player.f_19797_ % 100 == 0 && Perks.get(player, "earthbound") > 0) {
            ResourceLocation below = ForgeRegistries.BLOCKS.getKey(player.m_9236_().m_8055_(player.m_20097_()).m_60734_());
            if (below != null && (below.m_135815_().equals("grass_block") || below.m_135815_().equals("farmland"))) {
                player.m_5634_((float) Perks.get(player, "earthbound"));
            }
        }
        if (Perks.get(player, "seas_blessing") > 0 && player.m_20069_()) {
            player.m_7292_(new MobEffectInstance(MobEffects.f_19593_, 60, 0, true, false));
            player.m_7292_(new MobEffectInstance(MobEffects.f_19592_, 60, 0, true, false));
        }
    }

    @SubscribeEvent
    public void onLogout(PlayerEvent.PlayerLoggedOutEvent event) {
        if (event.getEntity() instanceof ServerPlayer player) {
            for (String key : new String[] {"speed", "toughness", "armor", "health", "attack_speed", "spell", "cooldown", "regen"}) {
                for (AttributeInstance instance : player.m_21204_().m_22145_()) {
                    instance.m_22120_(uuid(key));
                }
            }
        }
    }

    private static Attribute attribute(String namespace, String path) {
        return ForgeRegistries.ATTRIBUTES.getValue(new ResourceLocation(namespace, path));
    }

    private static UUID uuid(String key) {
        return UUID.nameUUIDFromBytes(("fotfskills:stat:" + key).getBytes());
    }

    /** Adds, updates or removes this stat's modifier so the attribute carries exactly value. */
    private static void set(ServerPlayer player, Attribute attribute, String key, double value, AttributeModifier.Operation op) {
        if (attribute == null) {
            return;
        }
        AttributeInstance instance = player.m_21051_(attribute);
        if (instance == null) {
            return;
        }
        UUID id = uuid(key);
        AttributeModifier old = instance.m_22111_(id);
        if (old != null && old.m_22218_() == value) {
            return;
        }
        if (old != null) {
            instance.m_22120_(id);
        }
        if (value != 0) {
            instance.m_22118_(new AttributeModifier(id, "fotfskills " + key, value, op));
        }
        if (attribute == Attributes.f_22276_ && player.m_21223_() > player.m_21233_()) {
            player.m_21153_(player.m_21233_());        // removing Iron Stomach health trims, never kills
        }
    }
}
```

Names to verify:
- `m_21204_` is getAttributes, and `m_22145_` is AttributeMap's sync/all-instances getter. If `m_22145_` isn't "all instances", use the attributes it can carry directly (the list in `set` calls); a Ruling is needed only if behaviour changes.
- `m_135815_` is ResourceLocation.getPath.

In `BlockPerks.onBroken`, after the XP update, add:

```java
        if (facts.hasTag("forge:ores") || facts.hasTag("minecraft:base_stone_overworld") || facts.hasTag("minecraft:base_stone_nether")) {
            CombatState.of(player).lastStoneMined = CombatState.now(player);
        }
```

Register `new ConditionalStats()` in `FotfSkills`.

- [ ] **Step 2: Build and test**
  - Run: `bash extras/fotfskills/test.sh && bash extras/fotfskills/build.sh`
  - Expected: all `ok`, `Built`.

- [ ] **Step 3: Commit**

```bash
git add extras/fotfskills
git commit -m "Skills 3a: situational stats (forest, combat, mining, saturation, weapon, spell power, Earthbound, Sea's Blessing)"
```

---

### Task 5: Wire the nodes

**Files:**
- Modify: `tools/skills/perks.json`, `tools/skills/test_make_skill_trees.py`

- [ ] **Step 1: Write the failing test**

```python
def test_weapon_and_conditional_nodes_are_wired():
    expect = {('mining', 'miners_might_2'): ('dmg_pickaxe_blunt', 0.3), ('forage', 'axe_mastery_1'): ('dmg_axe', 0.3),
              ('attack', 'heavy_arms_1'): ('pct_two_handed', 0.1), ('defense', 'second_wind_1'): ('second_wind', 1),
              ('agility', 'throwing_arm_1'): ('thrown_speed', 0.08), ('magic', 'staff_adept_1'): ('staff_cooldown', 0.04),
              ('cook', 'warriors_feast_1'): ('feast_spell', 0.1), ('fish', 'seas_blessing_1'): ('seas_blessing', 1)}
    for (tree_id, sid), (perk, value) in expect.items():
        defs = g.build_category(tree(tree_id), TIERS, XP, PERKS)['definitions.json']
        assert {'type': 'fotfskills:perk', 'data': {'perk': perk, 'value': value}} in defs[sid]['rewards'], sid
    magic = g.build_category(tree('magic'), TIERS, XP, PERKS)['definitions.json']
    assert {'type': 'puffish_skills:attribute', 'data': {'attribute': 'irons_spellbooks:spell_power', 'value': 0.1,
            'operation': 'multiply_base'}} in magic['battlemage_1']['rewards']
```

- [ ] **Step 2: Run it.**
  - Run: `python -m pytest -q -p no:cacheprovider tools/skills`
  - Expected: FAIL with KeyError 'rewards' on `miners_might_2`.

- [ ] **Step 3: Add these entries to `perks.json`**

`P(id, v)` is shorthand for `{"type": "fotfskills:perk", "data": {"perk": id, "value": v}}`, and `A(attr, v, op)` for a `puffish_skills:attribute` reward.

**Mining**

| Node | Reward(s) |
|---|---|
| miners_might | P(dmg_pickaxe_blunt, 0.3) |
| stonehide | P(stonehide, 1) |
| crusher | P(crush_armor, 1) |
| gem_focus | P(gem_spell, 0.02) |

**Forage**

| Node | Reward(s) |
|---|---|
| axe_mastery | P(dmg_axe, 0.3) |
| splitting_blow | P(armor_pierce_axe, 0.1) |
| forest_stride | P(forest_speed, 0.05) |
| bark_skin | P(forest_toughness, 0.5) |
| throwing_axes | P(pct_thrown_axe, 0.1) |
| berserkers_axe | P(berserker, 4) |

**Farm**

| Node | Reward(s) |
|---|---|
| reaper | P(dmg_scythe, 0.3) |
| grim_harvest | P(grim_harvest, 1) |
| earthbound | P(earthbound, 0.5) |

**Fish**

| Node | Reward(s) |
|---|---|
| trident_master | P(dmg_polearm, 0.3) |
| tidecaller | P(tide_spell, 0.04) |
| riptide_runner | A(forge:swim_speed, 0.1, multiply_base) |
| seas_blessing | P(seas_blessing, 1) |

**Cook**

| Node | Reward(s) |
|---|---|
| iron_stomach | P(iron_stomach, 2) |
| brain_food | P(brain_regen, 0.15) |
| warriors_feast | P(well_fed, 0.1) + P(feast_spell, 0.1) |

**Attack**

| Node | Reward(s) |
|---|---|
| footwork | P(combat_speed, 0.02) |
| spellblade | P(spellblade_mana, 1) |
| momentum | P(momentum, 0.05) |
| heavy_arms | P(pct_two_handed, 0.1) |
| duelist | P(duelist_speed, 0.08) |
| hunters_mark | P(hunters_mark, 0.05) |
| shield_bash | P(shield_bash, 0.2) |
| lifeline | P(lifeline, 1) |
| cleave | P(cleave, 0.3) |
| flurry | P(flurry, 1) |

**Range**

| Node | Reward(s) |
|---|---|
| eagle_eye | P(projectile_speed, 0.1) |
| thrower | P(pct_thrown, 0.08) |
| skirmisher | P(skirmish_speed, 0.1) |

**Defense**

| Node | Reward(s) |
|---|---|
| shield_thorns | P(shield_thorns, 0.08) |
| warded_mind | P(warded_spell, 0.01) |
| battlemage_plate | P(battlemage_mana, 2) |
| counter | P(counter, 0.15) |
| second_wind | P(second_wind, 1) |

**Agility**

| Node | Reward(s) |
|---|---|
| spring_step | P(jump_boost, 0.05) |
| light_weapons | P(light_speed, 0.04) |
| throwing_arm | P(thrown_speed, 0.08) + P(pct_thrown, 0.08) |

**Magic**

| Node | Reward(s) |
|---|---|
| staff_adept | P(staff_spell, 0.04) + P(staff_cooldown, 0.04) |
| battlemage | A(irons_spellbooks:spell_power, 0.1, multiply_base) |
| spellbound_steel | P(spellbound_steel, 0.1) |

- [ ] **Step 4: Run.**
  - Run: `python -m pytest -q -p no:cacheprovider tools/skills`
  - Expected: all passed (29).

- [ ] **Step 5: Commit**

```bash
python tools/skills/make_skill_trees.py
git add tools/skills config/puffish_skills
git commit -m "Skills 3a: weapon and conditional nodes wired"
```

---

### Task 6: Pack and boot

- [ ] **Step 1:** Update the sha512 in `mods/fotfskills.pw.toml`, run `packwiz refresh`, commit `Skills 3a: ship rebuilt add-on`, push, and reboot the test server with `PACK_REF=<sha>`.
- [ ] **Step 2:** Check the boot log. `docker logs fotf-test` must show `Mod configuration loaded successfully!` with no fotfskills, mixin or tag errors (`grep -iE "fotfskills|Couldn't load tag"`).
- [ ] **Step 3:** The in-game check is deferred to Dylan's playtest. Rows to add to the playtest list:
  - Axe Mastery hits harder with an axe.
  - Second Wind leaves 1 health once per 5 minutes.
  - Cleave splashes mobs but not pets.
  - Forest Stride is faster in forests.
  - Staff Adept raises spell power while holding a staff.
  - Spring Step jumps higher.
