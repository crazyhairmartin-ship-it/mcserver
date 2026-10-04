# Skills Phase 3b: Pets and Mounts Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the Taming tree and the cross-tree pet and mount nodes work, so a player can fight through their pets (spec).

The nodes covered:
- **Pet stats:** Bonded, Bonded II, Beastmaster, Alpha.
- **Pet combat:** Pack Tactics, Falconer, Loyal Guard, Guardian.
- **Pet care:** Caretaker, Pet Treats, Nature's Mend, Gentle Hand.
- **Breeding:** Breeder, Selective Breeding, Prized Stock.
- **Pet Scavenging.**
- **Mounts:** Mount Training, Rider, Saddler.

**Architecture:**
- **Pets:** an owned animal is any `OwnableEntity` whose owner is the player. That covers vanilla, modded and unicorn tamables plus tamed horses.
- **Stat buffs:** `PetPerks` refreshes pet and mount stats every second as transient attribute modifiers (shared `Modifiers` helper). Buffs apply to owned pets within 32 blocks of their online owner (spec) and to whatever a player rides. Buffs are cleared when the pet is out of range or the owner leaves.
- **Event hooks:** pet damage, guarding, feeding and taming.
- **Breeding:** `BreedingPerks` handles `BabyEntitySpawnEvent` (twins, faster growth, horse stats).
- **Pure logic:** `Scavenge` (loot table) and `Breeding` (stat rule) are unit-tested.
- **Guardian parties:** a small Open Parties and Claims bridge, registered only when OPAC is loaded.

**Tech Stack:** Java 17 javac in Docker against SRG names, Forge 47.4.23 events, Python generator + pytest, Pufferfish 0.19.1 `fotfskills:perk` rewards.

**Spec:** `docs/superpowers/specs/2026-10-03-skills-design.md`. Relevant parts: "Taming improves taming *and* makes pets strong", "Pet stats ... while you're within ~32 blocks", and "Pack tactics", "Pet scavenging", "Loyal Guard", "Guardian covers party members and pets".

## Global Constraints

- Pet buffs apply only while the owner is online and within 32 blocks. Nothing changes a pet permanently, except horse stats rolled at birth.
- Bonuses are opt-in power only. Pets never hurt players because of a perk. Falconer only sends pets at mobs the owner shot, and never at players or other owned animals.
- Perk ids live in `Perks.CAPS`. Node ids keep `<slug>_<k>`. Pufferfish stays pinned at 0.19.1.
- Every OPAC or Iron's class is touched only behind a `ModList.isLoaded` guard.
- After each add-on build, update the sha512 in `mods/fotfskills.pw.toml` and run `packwiz refresh`. Boot the test server with `PACK_REF=<pushed sha>`.

## Review Focus

1. **Buffs never stick.** Pets that walk out of range, are unloaded, or whose owner logs out lose every fotfskills modifier. Max health is trimmed and never kills.
2. **Two players and one horse.** The owner's Mount Training and the rider's Rider/Saddler add up, rather than one overwriting the other.
3. **Twins.** The second baby is a normal baby of the same species, gets the same growth and stats, and can't be produced without a real breeding.
4. **Gentle Hand.** It only tames after a real taming attempt (the taming item was used up) on an untamed animal. It gives Taming XP once.
5. **Loyal Guard / Guardian.** No damage loops, no infinite blocking (it's a chance per hit), and only living attackers count.

---

### Task 1: Pure pet logic

**Files:**
- Create: `extras/fotfskills/src/fotfskills/perk/Scavenge.java`, `extras/fotfskills/src/fotfskills/perk/Breeding.java`
- Create: `extras/fotfskills/test/fotfskills/perk/PetLogicTest.java`

**Interfaces:**
- Produces:
  - `Scavenge.pick(double roll) -> String`, an item id from a tiered table. `roll` is in [0,1): 70% common, 25% uncommon, 5% rare.
  - `Breeding.stat(double a, double b, boolean bonus, double vanillaMax, double prized) -> double`. It takes the better parent's value; a bonus raises it 5%. The result is capped at `vanillaMax`, or at `vanillaMax * (1 + prized)` with Prized Stock.

- [ ] **Step 1: Write the failing test** (`PetLogicTest.java`):

```java
package fotfskills.perk;

/** Pet scavenging table and horse stat inheritance. Run: sh test.sh */
public final class PetLogicTest {
    public static void main(String[] args) {
        check(Scavenge.pick(0.0).equals("minecraft:bone"), "lowest roll is the first common item");
        check(Scavenge.COMMON.contains(Scavenge.pick(0.69)), "under 0.70 is common");
        check(Scavenge.UNCOMMON.contains(Scavenge.pick(0.80)), "0.70-0.95 is uncommon");
        check(Scavenge.RARE.contains(Scavenge.pick(0.99)), "top 5% is rare");

        check(Breeding.stat(20, 26, false, 30, 0) == 26, "better parent's stat");
        check(Math.abs(Breeding.stat(20, 26, true, 30, 0) - 27.3) < 1e-9, "bonus +5%");
        check(Breeding.stat(29, 30, true, 30, 0) == 30, "capped at the vanilla max");
        check(Math.abs(Breeding.stat(29, 30, true, 30, 0.1) - 31.5) < 1e-9, "Prized Stock lifts the cap 10%");
        System.out.println("PetLogicTest ok");
    }

    private static void check(boolean ok, String what) {
        if (!ok) { System.out.println("FAIL: " + what); System.exit(1); }
    }
}
```

- [ ] **Step 2: Run it.**
  - Run: `bash extras/fotfskills/test.sh`
  - Expected: javac `cannot find symbol: class Scavenge` (and `Breeding`).

- [ ] **Step 3: Implement**

```java
package fotfskills.perk;

import java.util.List;

/** Pet Scavenging loot: what a pet may find and drop near its owner. Common 70%, uncommon 25%, rare 5%. */
public final class Scavenge {
    public static final List<String> COMMON = List.of("minecraft:bone", "minecraft:string", "minecraft:feather",
            "minecraft:leather", "minecraft:flint", "minecraft:stick", "minecraft:wheat_seeds", "minecraft:rabbit_hide");
    public static final List<String> UNCOMMON = List.of("minecraft:iron_nugget", "minecraft:gold_nugget", "minecraft:coal",
            "minecraft:slime_ball", "minecraft:honeycomb", "minecraft:amethyst_shard");
    public static final List<String> RARE = List.of("minecraft:emerald", "minecraft:diamond", "minecraft:name_tag",
            "minecraft:golden_apple");

    private Scavenge() {
    }

    public static String pick(double roll) {
        if (roll < 0.70) {
            return COMMON.get((int) (roll / 0.70 * COMMON.size()));
        }
        if (roll < 0.95) {
            return UNCOMMON.get((int) ((roll - 0.70) / 0.25 * UNCOMMON.size()));
        }
        return RARE.get(Math.min(RARE.size() - 1, (int) ((roll - 0.95) / 0.05 * RARE.size())));
    }
}
```

```java
package fotfskills.perk;

/** Selective Breeding / Prized Stock: a foal gets the better parent's stat, maybe +5%, capped (Prized Stock lifts the cap). */
public final class Breeding {
    private Breeding() {
    }

    public static double stat(double a, double b, boolean bonus, double vanillaMax, double prized) {
        double value = Math.max(a, b) * (bonus ? 1.05 : 1);
        return Math.min(value, vanillaMax * (1 + prized));
    }
}
```

- [ ] **Step 4: Run.**
  - Run: `bash extras/fotfskills/test.sh`
  - Expected: `PetLogicTest ok` plus the 7 earlier tests.

- [ ] **Step 5: Commit**

```bash
git add extras/fotfskills
git commit -m "Skills 3b: pet scavenging table and horse stat inheritance"
```

---

### Task 2: Pet and mount hooks

**Files:**
- Create in `extras/fotfskills/src/fotfskills/perk/`: `Modifiers.java`, `PetPerks.java`, `BreedingPerks.java`, `Parties.java`, `OpacParties.java`
- Modify: `Perks.java` (ids), `ConditionalStats.java` (use `Modifiers.set`), `IronsPerks.java` (Nature's Mend), `CombatState.java` (falcon target), `FotfSkills.java`

**Interfaces:**
- Consumes: `Perks.get/roll`, `CombatState` (markedTarget/markedUntil from 3a), `AmountSource.award(player, "tame", 1)` (2a), `Scavenge`, `Breeding`.
- Produces:
  - `Modifiers.set(LivingEntity, Attribute, String key, double value, AttributeModifier.Operation)`.
  - `PetPerks.healPets(ServerPlayer, double)`.
  - `Parties.same(MinecraftServer, UUID, UUID)`.

- [ ] **Step 1: Add these entries to `Perks.CAPS`**

```java
            Map.entry("pet_health", 1.0), Map.entry("pet_damage", 1.0), Map.entry("pet_armor", 20.0),
            Map.entry("pet_regen", 5.0), Map.entry("pet_speed", 1.0), Map.entry("pet_stun", 0.95),
            Map.entry("mount_speed", 1.0), Map.entry("mount_jump", 1.0), Map.entry("mount_health", 1.0),
            Map.entry("ride_speed", 1.0), Map.entry("ride_jump", 1.0), Map.entry("ride_armor", 20.0),
            Map.entry("pack_tactics", 2.0), Map.entry("falconer", 2.0), Map.entry("loyal_guard", 0.95),
            Map.entry("guardian", 0.9), Map.entry("caretaker", 20.0), Map.entry("pet_treats", 20.0),
            Map.entry("natures_mend", 5.0), Map.entry("gentle_hand", 0.95), Map.entry("breed_bonus", 0.95),
            Map.entry("twins", 0.95), Map.entry("growth", 0.9), Map.entry("prized_stock", 1.0), Map.entry("scavenging", 0.95)
```

- [ ] **Step 2: Write `Modifiers`.** Move `ConditionalStats.set` here, generalised to any `LivingEntity`. `ConditionalStats` then calls `Modifiers.set(player, ...)` and its private `set`/`uuid` are deleted.

```java
package fotfskills.perk;

import java.util.UUID;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.Attribute;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;

/** Transient attribute modifiers with fixed per-key UUIDs: add, update or remove so the entity carries exactly value. */
public final class Modifiers {
    private Modifiers() {
    }

    public static UUID uuid(String key) {
        return UUID.nameUUIDFromBytes(("fotfskills:stat:" + key).getBytes());
    }

    public static void set(LivingEntity entity, Attribute attribute, String key, double value, AttributeModifier.Operation op) {
        if (attribute == null) {
            return;
        }
        AttributeInstance instance = entity.m_21051_(attribute);
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
        if (attribute == Attributes.f_22276_ && entity.m_21223_() > entity.m_21233_()) {
            entity.m_21153_(entity.m_21233_());        // losing bonus health trims, never kills
        }
    }
}
```

- [ ] **Step 3: Write the parties bridge**

```java
package fotfskills.perk;

import java.util.UUID;
import java.util.function.BiPredicate;
import net.minecraft.server.MinecraftServer;

/** Whether two players share a party (Open Parties and Claims bridge, registered when OPAC is loaded). */
public final class Parties {
    private static BiPredicate<MinecraftServer, UUID[]> bridge = (server, ids) -> false;

    private Parties() {
    }

    public static void register(BiPredicate<MinecraftServer, UUID[]> partyCheck) {
        bridge = partyCheck;
    }

    public static boolean same(MinecraftServer server, UUID a, UUID b) {
        return bridge.test(server, new UUID[] {a, b});
    }
}
```

```java
package fotfskills.perk;

import java.util.UUID;
import net.minecraft.server.MinecraftServer;
import xaero.pac.common.server.api.OpenPACServerAPI;
import xaero.pac.common.server.parties.party.api.IServerPartyAPI;

/** Open Parties and Claims party check. Loaded only if openpartiesandclaims is present. */
public final class OpacParties {
    private OpacParties() {
    }

    public static boolean same(MinecraftServer server, UUID[] ids) {
        var parties = OpenPACServerAPI.get(server).getPartyManager();
        IServerPartyAPI a = parties.getPartyByMember(ids[0]);
        IServerPartyAPI b = parties.getPartyByMember(ids[1]);
        return a != null && b != null && a.getId().equals(b.getId());
    }
}
```

- [ ] **Step 4: Write `PetPerks`**

```java
package fotfskills.perk;

import fotfskills.xp.AmountSource;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.OwnableEntity;
import net.minecraft.world.entity.TamableAnimal;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.animal.Animal;
import net.minecraft.world.entity.animal.horse.AbstractHorse;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.Projectile;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.living.LivingAttackEvent;
import net.minecraftforge.event.entity.living.LivingHurtEvent;
import net.minecraftforge.event.entity.player.PlayerInteractEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.registries.ForgeRegistries;

/**
 * Taming tree and pet/mount nodes. Every second: owned pets within 32 blocks of their online owner, and anything a
 * player rides, get transient stat modifiers (Bonded, Bonded II, Beastmaster, Alpha, Mount Training, Rider, Saddler);
 * buffed animals that leave range lose them. Event hooks: Pack Tactics, Falconer, Alpha stun, Loyal Guard,
 * Guardian, Caretaker, Pet Treats, Gentle Hand, Pet Scavenging.
 */
public final class PetPerks {
    private static final String[] KEYS = {"pet_health", "pet_damage", "pet_armor", "pet_speed", "pet_jump"};
    /** Animals carrying fotfskills pet modifiers, so they can be cleared when no longer in range. */
    private final List<LivingEntity> buffed = new ArrayList<>();
    private record Attempt(ServerPlayer player, TamableAnimal animal, InteractionHand hand, Item item, int before) {
    }
    private final List<Attempt> attempts = new ArrayList<>();
    private long ticks;

    @SubscribeEvent
    public void onServerTick(TickEvent.ServerTickEvent event) {
        if (event.phase != TickEvent.Phase.END) {
            return;
        }
        resolveTamingAttempts();
        if (++ticks % 20 != 0) {
            return;
        }
        Map<LivingEntity, double[]> stats = new HashMap<>();   // health, damage, armor, speed, jump
        for (ServerPlayer player : event.getServer().m_6846_().m_11314_()) {
            for (LivingEntity pet : ownedNear(player, 32)) {
                double[] s = stats.computeIfAbsent(pet, p -> new double[5]);
                s[0] += Perks.get(player, "pet_health");
                s[1] += Perks.get(player, "pet_damage");
                s[2] += Perks.get(player, "pet_armor");
                s[3] += Perks.get(player, "pet_speed");
                if (pet instanceof AbstractHorse) {
                    s[0] += Perks.get(player, "mount_health");
                    s[3] += Perks.get(player, "mount_speed");
                    s[4] += Perks.get(player, "mount_jump");
                }
                double regen = Perks.get(player, "pet_regen");
                if (regen > 0 && ticks % 100 == 0) {
                    pet.m_5634_((float) regen);
                }
                if (ticks % 2400 == 0 && Perks.roll(player, "scavenging") && pet.m_20280_(player) < 16 * 16) {
                    scavenge(pet);
                }
            }
            if (player.m_20202_() instanceof LivingEntity mount) {
                double[] s = stats.computeIfAbsent(mount, p -> new double[5]);
                s[2] += Perks.get(player, "ride_armor");
                s[3] += Perks.get(player, "ride_speed");
                s[4] += Perks.get(player, "ride_jump");
            }
        }
        for (LivingEntity old : buffed) {
            if (!stats.containsKey(old) && !old.m_213877_()) {
                apply(old, new double[5]);
            }
        }
        buffed.clear();
        stats.forEach((animal, s) -> {
            apply(animal, s);
            buffed.add(animal);
        });
    }

    private static void apply(LivingEntity animal, double[] s) {
        Modifiers.set(animal, Attributes.f_22276_, KEYS[0], s[0], AttributeModifier.Operation.MULTIPLY_BASE);
        Modifiers.set(animal, Attributes.f_22281_, KEYS[1], s[1], AttributeModifier.Operation.MULTIPLY_BASE);
        Modifiers.set(animal, Attributes.f_22284_, KEYS[2], s[2], AttributeModifier.Operation.ADDITION);
        Modifiers.set(animal, Attributes.f_22279_, KEYS[3], s[3], AttributeModifier.Operation.MULTIPLY_BASE);
        Modifiers.set(animal, Attributes.f_22288_, KEYS[4], s[4], AttributeModifier.Operation.MULTIPLY_BASE);
    }

    /** The player's owned animals within range (any OwnableEntity: tamed pets, tamed horses, modded companions). */
    static List<LivingEntity> ownedNear(ServerPlayer player, double range) {
        List<LivingEntity> out = new ArrayList<>();
        for (LivingEntity entity : player.m_9236_().m_45976_(LivingEntity.class, player.m_20191_().m_82400_(range))) {
            if (entity instanceof OwnableEntity pet && player.m_20148_().equals(pet.m_21805_()) && entity.m_6084_()) {
                out.add(entity);
            }
        }
        return out;
    }

    private static ServerPlayer owner(Entity entity) {
        return entity instanceof OwnableEntity pet && pet.m_269323_() instanceof ServerPlayer player ? player : null;
    }

    private static void scavenge(LivingEntity pet) {
        Item item = ForgeRegistries.ITEMS.getValue(new ResourceLocation(Scavenge.pick(Perks.random())));
        if (item != null) {
            pet.m_9236_().m_7967_(new ItemEntity(pet.m_9236_(), pet.m_20185_(), pet.m_20186_() + 0.5, pet.m_20189_(), new ItemStack(item)));
        }
    }

    @SubscribeEvent(priority = EventPriority.LOW)
    public void onHurt(LivingHurtEvent event) {
        LivingEntity target = event.getEntity();
        Entity attacker = event.getSource().m_7639_();
        Entity direct = event.getSource().m_7640_();
        float amount = event.getAmount();

        // Falconer: the owner's arrow marks the target and sends nearby pets at it.
        if (attacker instanceof ServerPlayer shooter && direct instanceof Projectile && owner(target) == null
                && !(target instanceof Player) && Perks.get(shooter, "falconer") > 0) {
            CombatState state = CombatState.of(shooter);
            state.falconTarget = target.m_20148_();
            state.falconUntil = CombatState.now(shooter) + 200;
            for (LivingEntity pet : ownedNear(shooter, 24)) {
                if (pet instanceof Mob mob && !(pet instanceof TamableAnimal sitter && sitter.m_21827_())) {
                    mob.m_6710_(target);
                }
            }
        }

        // Pack Tactics (owner's melee target) and Falconer (owner's arrow target) damage; Alpha stun.
        ServerPlayer petOwner = owner(attacker);
        if (petOwner != null && target != petOwner) {
            CombatState state = CombatState.of(petOwner);
            long now = CombatState.now(petOwner);
            double pct = 0;
            if (target.m_20148_().equals(state.markedTarget) && now <= state.markedUntil) {
                pct += Perks.get(petOwner, "pack_tactics");
            }
            if (target.m_20148_().equals(state.falconTarget) && now <= state.falconUntil) {
                pct += Perks.get(petOwner, "falconer");
            }
            amount *= (float) (1 + pct);
            if (Perks.roll(petOwner, "pet_stun")) {
                target.m_7292_(new MobEffectInstance(MobEffects.f_19597_, 20, 3, false, true));
            }
        }

        // Guardian: pets and party members near you take less damage.
        double guard = 0;
        ServerPlayer targetOwner = owner(target);
        if (targetOwner != null && targetOwner.m_20280_(target) < 64) {
            guard = Perks.get(targetOwner, "guardian");
        } else if (target instanceof ServerPlayer hurt) {
            for (ServerPlayer friend : hurt.m_284548_().m_6907_()) {
                if (friend != hurt && friend.m_20280_(hurt) < 64
                        && Parties.same(hurt.m_20194_(), hurt.m_20148_(), friend.m_20148_())) {
                    guard = Math.max(guard, Perks.get(friend, "guardian"));
                }
            }
        }
        event.setAmount((float) (amount * (1 - guard)));
    }

    /** Loyal Guard: a nearby pet leaps in and takes nothing; the hit is cancelled for you. */
    @SubscribeEvent
    public void onAttack(LivingAttackEvent event) {
        if (!(event.getEntity() instanceof ServerPlayer player) || !(event.getSource().m_7639_() instanceof LivingEntity attacker)
                || attacker == player || Perks.get(player, "loyal_guard") <= 0) {
            return;
        }
        List<LivingEntity> pets = ownedNear(player, 8);
        if (!pets.isEmpty() && Perks.roll(player, "loyal_guard")) {
            event.setCanceled(true);
            LivingEntity pet = pets.get(0);
            if (pet instanceof Mob mob && !(attacker instanceof Player)) {
                mob.m_6710_(attacker);
            }
        }
    }

    /** Caretaker / Pet Treats when feeding your own pet; Gentle Hand when trying to tame. */
    @SubscribeEvent
    public void onInteract(PlayerInteractEvent.EntityInteract event) {
        if (!(event.getEntity() instanceof ServerPlayer player) || !(event.getTarget() instanceof Animal animal)) {
            return;
        }
        ItemStack held = player.m_21120_(event.getHand());
        if (held.m_41619_()) {
            return;
        }
        if (animal instanceof OwnableEntity pet && player.m_20148_().equals(pet.m_21805_()) && animal.m_6898_(held)) {
            animal.m_5634_((float) Perks.get(player, "caretaker"));
            double treat = Perks.get(player, "pet_treats");
            if (treat > 0) {
                animal.m_7292_(new MobEffectInstance(MobEffects.f_19605_, (int) (treat * 20), 0, false, true));
            }
        }
        if (animal instanceof TamableAnimal tamable && !tamable.m_21824_() && Perks.get(player, "gentle_hand") > 0) {
            attempts.add(new Attempt(player, tamable, event.getHand(), held.m_41720_(), held.m_41613_()));
        }
    }

    /** One tick after a taming attempt: if the taming item was used up but the animal is still wild, roll Gentle Hand. */
    private void resolveTamingAttempts() {
        if (attempts.isEmpty()) {
            return;
        }
        for (Attempt a : attempts) {
            ItemStack now = a.player.m_21120_(a.hand);
            int count = now.m_150930_(a.item) ? now.m_41613_() : 0;
            if (count == a.before - 1 && !a.animal.m_21824_() && a.animal.m_6084_() && Perks.roll(a.player, "gentle_hand")) {
                a.animal.m_21828_(a.player);
                a.animal.m_21839_(true);
                a.animal.m_9236_().m_7605_(a.animal, (byte) 7);     // hearts
                AmountSource.award(a.player, "tame", 1);
            }
        }
        attempts.clear();
    }

    /** Nature's Mend: called when the player casts a healing spell. */
    public static void healPets(ServerPlayer player, double amount) {
        if (amount > 0) {
            for (LivingEntity pet : ownedNear(player, 8)) {
                pet.m_5634_((float) amount);
            }
        }
    }
}
```

Names to verify with javap:
- `m_6084_` isAlive.
- `m_284548_` getLevel on ServerPlayer (or `serverLevel()`), and `m_6907_` players.
- `m_20194_` getServer.

If `m_284548_` isn't ServerPlayer.serverLevel(), use `(ServerLevel) hurt.m_9236_()`.

Add to `CombatState`:

```java
    public UUID falconTarget;
    public long falconUntil;
```

- [ ] **Step 5: Write `BreedingPerks`**

```java
package fotfskills.perk;

import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.AgeableMob;
import net.minecraft.world.entity.ai.attributes.Attribute;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.animal.horse.AbstractHorse;
import net.minecraftforge.event.entity.living.BabyEntitySpawnEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;

/** Breeder (twins, faster growth), Selective Breeding and Prized Stock (foal stats) on player-caused breeding. */
public final class BreedingPerks {
    private static final Attribute[] HORSE_STATS = {Attributes.f_22276_, Attributes.f_22279_, Attributes.f_22288_};
    private static final double[] VANILLA_MAX = {30, 0.3375, 1.0};

    @SubscribeEvent(priority = EventPriority.LOW)
    public void onBaby(BabyEntitySpawnEvent event) {
        if (event.isCanceled() || !(event.getCausedByPlayer() instanceof ServerPlayer player) || event.getChild() == null
                || !(event.getParentA() instanceof AgeableMob a) || !(event.getParentB() instanceof AgeableMob b)) {
            return;
        }
        AgeableMob child = event.getChild();
        shape(player, child, a, b);
        if (Perks.roll(player, "twins") && a.m_9236_() instanceof ServerLevel level) {
            AgeableMob twin = a.m_142606_(level, b);
            if (twin != null) {
                twin.m_6863_(true);
                twin.m_7678_(a.m_20185_(), a.m_20186_(), a.m_20189_(), 0, 0);
                shape(player, twin, a, b);
                level.m_7967_(twin);
            }
        }
    }

    /** Faster growth for every baby; better-parent stats (and bonuses) for foals. */
    private static void shape(ServerPlayer player, AgeableMob child, AgeableMob a, AgeableMob b) {
        double growth = Perks.get(player, "growth");
        if (growth > 0) {
            child.m_146762_((int) (-24000 * (1 - growth)));
        }
        if (Perks.get(player, "breed_bonus") > 0 && child instanceof AbstractHorse && a instanceof AbstractHorse && b instanceof AbstractHorse) {
            double prized = Perks.get(player, "prized_stock");
            for (int i = 0; i < HORSE_STATS.length; i++) {
                AttributeInstance ci = child.m_21051_(HORSE_STATS[i]);
                AttributeInstance ai = a.m_21051_(HORSE_STATS[i]);
                AttributeInstance bi = b.m_21051_(HORSE_STATS[i]);
                if (ci != null && ai != null && bi != null) {
                    ci.m_22100_(Breeding.stat(ai.m_22115_(), bi.m_22115_(), Perks.roll(player, "breed_bonus"), VANILLA_MAX[i], prized));
                }
            }
            child.m_21153_(child.m_21233_());
        }
    }
}
```

`m_6863_` is AgeableMob.setBaby; verify it.

- [ ] **Step 6: Wire everything**
  - In `IronsPerks.onCast`, inside the caster branch, add:

    ```java
    if (event.getSpellId().contains("heal")) {
        PetPerks.healPets(caster, 2 * event.getSpellLevel() * Perks.get(caster, "natures_mend"));
    }
    ```

  - In `FotfSkills`, register `new PetPerks()` and `new BreedingPerks()`. Add `if (ModList.get().isLoaded("openpartiesandclaims")) { Parties.register(OpacParties::same); }`.
  - In `ConditionalStats`, replace its private `set`/`uuid` with `Modifiers.set`/`Modifiers.uuid`.

- [ ] **Step 7: Build and test.**
  - Run: `bash extras/fotfskills/test.sh && bash extras/fotfskills/build.sh`
  - Expected: all tests `ok`, `Built`.

- [ ] **Step 8: Commit**

```bash
git add extras/fotfskills
git commit -m "Skills 3b: pet and mount perks (stats, pack tactics, falconer, guards, care, taming, breeding, scavenging)"
```

---

### Task 3: Wire the nodes

**Files:**
- Modify: `tools/skills/perks.json`, `tools/skills/test_make_skill_trees.py`

- [ ] **Step 1: Write the failing test**

```python
def test_pet_and_mount_nodes_are_wired():
    expect = {('taming', 'bonded_3'): ('pet_health', 0.05), ('taming', 'alpha_1'): ('pet_stun', 0.1),
              ('taming', 'breeder_2'): ('twins', 0.06), ('taming', 'gentle_hand_1'): ('gentle_hand', 0.1),
              ('range', 'falconer_1'): ('falconer', 0.05), ('defense', 'guardian_1'): ('guardian', 0.05),
              ('agility', 'rider_1'): ('ride_speed', 0.04), ('craft', 'saddler_1'): ('ride_armor', 2),
              ('cook', 'pet_treats_1'): ('pet_treats', 5), ('magic', 'natures_mend_1'): ('natures_mend', 1)}
    for (tree_id, sid), (perk, value) in expect.items():
        defs = g.build_category(tree(tree_id), TIERS, XP, PERKS)['definitions.json']
        assert {'type': 'fotfskills:perk', 'data': {'perk': perk, 'value': value}} in defs[sid]['rewards'], sid
```

- [ ] **Step 2: Run.**
  - Run: `python -m pytest -q -p no:cacheprovider tools/skills`
  - Expected: FAIL (KeyError 'rewards').

- [ ] **Step 3: Add these entries to `perks.json`** (`P(id, v)` as in earlier plans)

**Taming**

| Node | Reward(s) |
|---|---|
| gentle_hand | P(gentle_hand, 0.1) |
| selective_breeding | P(breed_bonus, 0.02) |
| bonded | P(pet_health, 0.05) |
| pet_scavenging | P(scavenging, 0.1) |
| beastmaster | P(pet_damage, 0.15) |
| breeder | P(twins, 0.06) + P(growth, 0.1) |
| pack_tactics | P(pack_tactics, 0.1) |
| loyal_guard | P(loyal_guard, 0.08) |
| mount_training | P(mount_speed, 0.04) + P(mount_jump, 0.04) + P(mount_health, 0.04) |
| bonded_ii | P(pet_armor, 2) + P(pet_regen, 0.5) |
| caretaker | P(caretaker, 2) |
| alpha | P(pet_health, 0.3) + P(pet_damage, 0.3) + P(pet_speed, 0.3) + P(pet_stun, 0.1) |
| prized_stock | P(prized_stock, 0.1) |

**Other trees**

| Tree | Node | Reward(s) |
|---|---|---|
| range | falconer | P(falconer, 0.05) |
| defense | guardian | P(guardian, 0.05) |
| agility | rider | P(ride_speed, 0.04) + P(ride_jump, 0.04) |
| craft | saddler | P(ride_speed, 0.05) + P(ride_armor, 2) |
| cook | pet_treats | P(pet_treats, 5) |
| magic | natures_mend | P(natures_mend, 1) |

Bloodlines (rare colours/variants) stays unwired. Variants are mod-specific, so it's a Ruling. Soul Mender belongs to phase 4 (pet revival).

- [ ] **Step 4: Run.**
  - Run: `python -m pytest -q -p no:cacheprovider tools/skills`
  - Expected: all passed (30).

- [ ] **Step 5: Commit**

```bash
python tools/skills/make_skill_trees.py
git add tools/skills config/puffish_skills
git commit -m "Skills 3b: pet and mount nodes wired"
```

---

### Task 4: Pack and boot

- [ ] **Step 1:** Update the jar sha512 and run `packwiz refresh`. Commit `Skills 3b: ship rebuilt add-on`, push, and reboot the test server with `PACK_REF=<sha>`.
- [ ] **Step 2:** The boot log must show `Mod configuration loaded successfully!` with no fotfskills or mixin errors.
- [ ] **Step 3:** In-game rows go on Dylan's playtest list:
  - Bonded raises wolf health while you're near.
  - Pack Tactics: the wolf hits your target harder.
  - Falconer: wolves chase what you shoot.
  - Gentle Hand: bones tame more often.
  - Breeder: sometimes twins.
  - Mount Training: a tamed horse is faster near you.
