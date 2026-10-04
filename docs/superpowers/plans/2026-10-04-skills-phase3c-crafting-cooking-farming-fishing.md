# Skills Phase 3c: Crafting, Cooking, Farming and Fishing Perks Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the remaining gathering, crafting, cooking and fishing nodes work. The nodes, by tree:

| Tree | Nodes |
|---|---|
| Mining | Smelter (auto-smelt), Ore Nose |
| Foraging | Berry Picker, Beekeeper |
| Farming | Green Thumb, Gardener, Fertile Soil I/II, Harvest Feast, Sweeping Harvest, Compost King |
| Fishing | Lucky Line, Treasure Hunter, Leviathan Bait, Hook Shot, Sushi Chef, Sea Legs |
| Cooking | Thrifty Cook I/II, Hearty Meals, Chef, Trail Rations, Picnic |
| Crafting | Smith, Whetstone, Weaponsmith, Armourer, Enchanted Crafts I/II, Masterwork, Book Saver, Repair Kit, Spellwright |

**Architecture:** Four hook classes in the add-on, each covering one area:

- **`FarmPerks`** handles crop placing, growth near the player, right-click harvests (checked the next tick), composters, beehives and scythe sweeps.
- **`FoodPerks`** handles eating effects and Trail Rations. Trail Rations is a `Player.causeFoodExhaustion` mixin.
- **`FishingPerks`** handles hook hits, trophies and boat speed. Boat speed is applied on the driver's client from synced perk totals.
- **`CraftPerks`** handles crafted gear: enchantments, durability NBT, item attribute modifiers, Book Saver and Repair Kit.

Supporting pieces:

- **Auto-smelt and Ore Nose** go into `BlockPerks.onBroken`.
- **Ingredient refunds** for cooking and spell items extend the existing `ItemPerks.onCraft`.
- **Lucky Line and Treasure Hunter** are plain `minecraft:generic.luck` attribute rewards (fishing loot uses player luck).
- **Pure math** (boat friction, enchantment level roll) lives in `Tuning` and is unit-tested.

**Tech Stack:** Java 17 javac in Docker against SRG names, Forge 47.4.23 events and mixins, Python generator + pytest, Pufferfish 0.19.1.

**Spec:** `docs/superpowers/specs/2026-10-03-skills-design.md`. Relevant parts: "Perk types" (saving, extra output, activity boosts) and "Unique and conditional" (Auto-smelt, Treasure sense, Hearty meals, Green thumb, Enchanted crafts, Book saver). Also rev 4: "Crafting power is guaranteed" (Enchanted Crafts always adds an enchantment; Weaponsmith always +1 attack damage; Armourer always +1 toughness; Masterwork always two).

## Global Constraints

- Crafting power is guaranteed, not a roll: Enchanted Crafts, Weaponsmith, Armourer and Masterwork always apply. Resource saving stays a chance.
- No duplication loops:
  - Refunds keep the 2b rules (CraftingContainer, 2+ item types, no tools, unstackables or NBT stacks).
  - Item stat bonuses apply once per item, using an NBT marker. Repairing again never stacks Whetstone.
  - Auto-smelt only converts the block's own fresh drops.
- Placed blocks give no gathering perks. That's already handled in `BlockPerks.onBroken`, which the sweep reuses through `ServerPlayerGameMode.destroyBlock`.
- Perk ids live in `Perks.CAPS`. Node ids keep `<slug>_<k>`. Pufferfish stays pinned at 0.19.1.
- After each add-on build, update the sha512 in `mods/fotfskills.pw.toml` and run `packwiz refresh`. Boot the test server with `PACK_REF=<pushed sha>`.

## Deferred (Rulings, not wired in 3c)

These depend on internals of one mod, or on furnaces and other block machines that don't belong to a player. They wait for the tuning phase:
- **Tunnel Vision:** FTB Ultimine hunger.
- **Long Net:** butterfly net reach.
- **Bait Saver and Lure Master:** Aquaculture bait and lures.
- **Brewer:** Let's Do drinks.
- **Feast Maker:** Farmer's Delight feast blocks.
- **Quick Hands and Crafting's Smelter:** cooking-station and furnace speed.
- **Salvager:** grindstones.
- **Irrigator:** farmland moisture radius, a block rule rather than a player perk.

Earthshaker, Reaper's Due and Druid's Grove move to 3d (combat and magic).

## Review Focus

1. **Sweeping Harvest recursion.** The 3x3/5x5 sweep goes through `destroyBlock`, which re-enters `onBroken`. A guard must stop it from sweeping again. It only breaks mature crops, and claims still apply.
2. **Item attribute modifiers.** Adding a modifier to an item's NBT turns off its default attributes. The default modifiers for that slot must be copied in first, or a sword loses its base damage.
3. **Auto-smelt** only changes drops that this break spawned this tick at that block, never nearby items. Silk Touch never auto-smelts.
4. **Next-tick checks** (berries, honey, composter) only pay out when the block really changed after the player's right-click, once.
5. **Sea Legs** runs on the client for the boat's driver only, and can't compound into runaway speed.

---

### Task 1: Pure tuning math

**Files:**
- Create: `extras/fotfskills/src/fotfskills/perk/Tuning.java`, `extras/fotfskills/test/fotfskills/perk/TuningTest.java`

**Interfaces:**
- Produces:
  - `Tuning.boatFactor(double faster) -> double`. This is the per-tick horizontal velocity factor that raises a boat's top speed on water by `faster` (water friction 0.9, so factor = (1 - 0.1/(1+faster)) / 0.9).
  - `Tuning.enchantLevel(int cap, int bonus, int maxLevel, double roll) -> int`. The level is uniform in 1..cap, then plus `bonus`, clamped to 1..maxLevel.

- [ ] **Step 1: Write the failing test**

```java
package fotfskills.perk;

/** Sea Legs boat friction and Enchanted Crafts level rolls. Run: sh test.sh */
public final class TuningTest {
    public static void main(String[] args) {
        check(Math.abs(Tuning.boatFactor(0) - 1.0) < 1e-9, "no perk, no change");
        double f = Tuning.boatFactor(0.1);
        // top speed with friction 0.9*f relative to 0.9: (1-0.9)/(1-0.9*f) should be 1.1
        check(Math.abs((1 - 0.9) / (1 - 0.9 * f) - 1.1) < 1e-9, "10% faster top speed");
        check(Tuning.enchantLevel(1, 0, 5, 0.99) == 1, "Enchanted Crafts I: always level I");
        check(Tuning.enchantLevel(3, 0, 5, 0.99) == 3 && Tuning.enchantLevel(3, 0, 5, 0.0) == 1, "rank III: up to III");
        check(Tuning.enchantLevel(3, 2, 4, 0.99) == 4, "Enchanted Crafts II adds levels, capped at the max");
        check(Tuning.enchantLevel(3, 1, 1, 0.5) == 1, "single-level enchantments stay at I");
        System.out.println("TuningTest ok");
    }

    private static void check(boolean ok, String what) {
        if (!ok) { System.out.println("FAIL: " + what); System.exit(1); }
    }
}
```

- [ ] **Step 2: Run it.**
  - Run: `bash extras/fotfskills/test.sh`
  - Expected: `cannot find symbol: class Tuning`.

- [ ] **Step 3: Implement**

```java
package fotfskills.perk;

/** Small formulas for Sea Legs and Enchanted Crafts. */
public final class Tuning {
    private Tuning() {
    }

    /** Per-tick horizontal velocity factor that makes a boat's top speed on water (friction 0.9) 1 + faster times higher. */
    public static double boatFactor(double faster) {
        return (1 - 0.1 / (1 + faster)) / 0.9;
    }

    /** A level uniform in 1..cap, plus bonus, within 1..maxLevel. */
    public static int enchantLevel(int cap, int bonus, int maxLevel, double roll) {
        int level = 1 + (int) Math.floor(roll * Math.max(cap, 1)) + bonus;
        return Math.max(1, Math.min(level, maxLevel));
    }
}
```

- [ ] **Step 4: Run.**
  - Run: `bash extras/fotfskills/test.sh`
  - Expected: `TuningTest ok` plus the 9 earlier tests.

- [ ] **Step 5: Commit**

```bash
git add extras/fotfskills
git commit -m "Skills 3c: boat friction and enchantment level math"
```

---

### Task 2: Hooks

**Files:**
- Create in `extras/fotfskills/src/fotfskills/perk/`: `FarmPerks.java`, `FoodPerks.java`, `FishingPerks.java`, `CraftPerks.java`
- Create: `extras/fotfskills/src/fotfskills/mixin/PlayerExhaustionMixin.java`
- Modify:
  - `Perks.java` (ids)
  - `BlockPerks.java` (auto-smelt, Ore Nose, sweep call)
  - `ItemPerks.java` (cook/spell refunds)
  - `mixin/ItemStackDurabilityMixin.java` (Smith NBT)
  - `res/fotfskills.mixins.json`
  - `FotfSkills.java`

**Interfaces:**
- Consumes: `Perks`, `Chance`, `Tuning`, `Weapons`, `Parties`, `BlockFacts`, `PlacedBlocks`, `BlockPerks.onBroken`.
- Produces:
  - `FarmPerks.sweep(ServerPlayer, BlockPos, BlockState)`, called from `onBroken` for mature crops.
  - `CraftPerks.improve(ServerPlayer, ItemStack)`.

- [ ] **Step 1: Add these entries to `Perks.CAPS`**

```java
            Map.entry("autosmelt", 0.95), Map.entry("ore_nose", 0.95), Map.entry("berry_picker", 0.95),
            Map.entry("beekeeper", 0.95), Map.entry("green_thumb", 0.95), Map.entry("fertile_soil", 2.0),
            Map.entry("harvest_feast", 2.0), Map.entry("sweeping_harvest", 2.0), Map.entry("compost_king", 0.95),
            Map.entry("hook_shot", 10.0), Map.entry("sushi_chef", 10.0), Map.entry("leviathan", 0.2),
            Map.entry("sea_legs", 1.0), Map.entry("cook_save", 0.95), Map.entry("hearty_meals", 2.0),
            Map.entry("chef", 2.0), Map.entry("trail_rations", 0.9), Map.entry("picnic", 10.0),
            Map.entry("smith", 0.95), Map.entry("whetstone", 5.0), Map.entry("weaponsmith", 5.0),
            Map.entry("armourer", 5.0), Map.entry("enchant_level", 5.0), Map.entry("enchant_bonus", 5.0),
            Map.entry("masterwork", 1.0), Map.entry("book_saver", 1.0), Map.entry("repair_kit", 0.9),
            Map.entry("spell_save", 0.95)
```

- [ ] **Step 2: Write `FarmPerks`**

```java
package fotfskills.perk;

import java.util.ArrayList;
import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.NeutralMob;
import net.minecraft.world.entity.animal.Bee;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.BeehiveBlock;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.ComposterBlock;
import net.minecraft.world.level.block.CropBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.IntegerProperty;
import net.minecraft.world.level.block.state.properties.Property;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.player.PlayerInteractEvent;
import net.minecraftforge.event.level.BlockEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.registries.ForgeRegistries;

/**
 * Farming and foraging extras: Green Thumb (planted crops start a stage later), Fertile Soil (crops near you get extra
 * growth ticks), Sweeping Harvest (scythes reap mature crops around the broken one), and right-click harvests checked
 * one tick later: Berry Picker (a bush's age went down: berries picked), Beekeeper (a full hive was emptied), Compost
 * King (a composter filled a layer).
 */
public final class FarmPerks {
    private record Click(ServerPlayer player, ServerLevel level, BlockPos pos, BlockState before) {
    }

    private final List<Click> clicks = new ArrayList<>();
    private static boolean sweeping;

    @SubscribeEvent(priority = EventPriority.LOWEST)
    public void onPlace(BlockEvent.EntityPlaceEvent event) {
        if (event.isCanceled() || !(event.getEntity() instanceof ServerPlayer player)
                || !(event.getPlacedBlock().m_60734_() instanceof CropBlock crop) || !Perks.roll(player, "green_thumb")) {
            return;
        }
        BlockState placed = event.getPlacedBlock();
        IntegerProperty age = age(placed);
        if (age != null && placed.m_61143_(age) < max(age)) {
            event.getLevel().m_7731_(event.getPos(), placed.m_61124_(age, placed.m_61143_(age) + 1), 3);
        }
    }

    /** Fertile Soil: extra random ticks on crops around the player (about 20 attempts a second per 1.0). */
    @SubscribeEvent
    public void onPlayerTick(TickEvent.PlayerTickEvent event) {
        if (event.phase != TickEvent.Phase.END || !(event.player instanceof ServerPlayer player) || player.f_19797_ % 20 != 0) {
            return;
        }
        double fertile = Perks.get(player, "fertile_soil");
        if (fertile <= 0 || !(player.m_9236_() instanceof ServerLevel level)) {
            return;
        }
        int tries = (int) Math.round(fertile * 20);
        BlockPos center = player.m_20183_();
        for (int i = 0; i < tries; i++) {
            BlockPos pos = center.m_7918_(level.f_46441_.m_188503_(9) - 4, level.f_46441_.m_188503_(3) - 1, level.f_46441_.m_188503_(9) - 4);
            BlockState state = level.m_8055_(pos);
            if (state.m_60734_() instanceof CropBlock && state.m_60823_()) {
                state.m_222972_(level, pos, level.f_46441_);
            }
        }
    }

    /** Sweeping Harvest: called from BlockPerks.onBroken for a mature crop broken with a scythe. */
    public static void sweep(ServerPlayer player, BlockPos pos, BlockState state) {
        int radius = (int) Math.round(Perks.get(player, "sweeping_harvest"));
        if (sweeping || radius <= 0 || !Weapons.is(player.m_21205_(), "scythe")) {
            return;
        }
        sweeping = true;
        try {
            for (int dx = -radius; dx <= radius; dx++) {
                for (int dz = -radius; dz <= radius; dz++) {
                    BlockPos other = pos.m_7918_(dx, 0, dz);
                    if ((dx != 0 || dz != 0) && new BlockFacts(player.m_9236_().m_8055_(other)).matureCrop()) {
                        player.f_8941_.m_9280_(other);      // through the game mode: claims, XP and drop perks apply
                    }
                }
            }
        } finally {
            sweeping = false;
        }
    }

    @SubscribeEvent
    public void onRightClick(PlayerInteractEvent.RightClickBlock event) {
        if (event.getEntity() instanceof ServerPlayer player && event.getLevel() instanceof ServerLevel level) {
            BlockState state = level.m_8055_(event.getPos());
            if (age(state) != null || state.m_60734_() instanceof BeehiveBlock || state.m_60734_() instanceof ComposterBlock) {
                clicks.add(new Click(player, level, event.getPos(), state));
            }
        }
    }

    @SubscribeEvent
    public void onServerTick(TickEvent.ServerTickEvent event) {
        if (event.phase != TickEvent.Phase.END || clicks.isEmpty()) {
            return;
        }
        for (Click c : new ArrayList<>(clicks)) {
            BlockState now = c.level.m_8055_(c.pos);
            if (now.m_60734_() != c.before.m_60734_()) {
                continue;
            }
            Block block = now.m_60734_();
            if (block instanceof ComposterBlock) {
                int before = c.before.m_61143_(ComposterBlock.f_51913_);
                int after = now.m_61143_(ComposterBlock.f_51913_);
                if (after == before + 1 && after < 7 && Perks.roll(c.player, "compost_king")) {
                    c.level.m_7731_(c.pos, now.m_61124_(ComposterBlock.f_51913_, after + 1), 3);
                }
            } else if (block instanceof BeehiveBlock) {
                if (c.before.m_61143_(BeehiveBlock.f_49564_) == 5 && now.m_61143_(BeehiveBlock.f_49564_) == 0
                        && Perks.get(c.player, "beekeeper") > 0) {
                    if (Perks.roll(c.player, "beekeeper")) {
                        Block.m_49840_(c.level, c.pos, new ItemStack(ForgeRegistries.ITEMS.getValue(new ResourceLocation("minecraft", "honeycomb")), 2));
                    }
                    for (Bee bee : c.level.m_45976_(Bee.class, c.player.m_20191_().m_82400_(16))) {
                        bee.m_21662_();                 // bees stay calm
                    }
                }
            } else if (!(block instanceof CropBlock)) {
                IntegerProperty age = age(now);
                if (age != null && c.before.m_61143_(age) > now.m_61143_(age) && Perks.roll(c.player, "berry_picker")) {
                    Block.m_49840_(c.level, c.pos, block.m_7397_(c.level, c.pos, c.before));
                }
            }
        }
        clicks.clear();
    }

    private static IntegerProperty age(BlockState state) {
        for (Property<?> property : state.m_61147_()) {
            if (property instanceof IntegerProperty age && age.m_61708_().equals("age")) {
                return age;
            }
        }
        return null;
    }

    private static int max(IntegerProperty age) {
        return age.m_6908_().stream().max(Integer::compare).orElse(0);
    }
}
```

`m_7918_` is BlockPos.offset(int,int,int) and `m_188503_` is RandomSource.nextInt(int); check both with javap.

- [ ] **Step 3: Write `FoodPerks` and the exhaustion mixin**

```java
package fotfskills.perk;

import com.mojang.datafixers.util.Pair;
import java.util.Set;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.tags.TagKey;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.food.FoodData;
import net.minecraft.world.food.FoodProperties;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.event.entity.living.LivingEntityUseItemEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.registries.ForgeRegistries;

/**
 * Eating: Hearty Meals (extra saturation), Chef (the meal's effects last longer), Harvest Feast (crop foods fill more),
 * Sushi Chef (fish foods give Water Breathing and saturation), Picnic (heals you and party members nearby).
 */
public final class FoodPerks {
    private static final Set<String> CROP_TAGS = Set.of("forge:vegetables", "forge:fruits", "forge:crops", "forge:bread");
    private static final Set<String> FISH_TAGS = Set.of("forge:raw_fishes", "forge:cooked_fishes", "minecraft:fishes");

    @SubscribeEvent
    public void onEat(LivingEntityUseItemEvent.Finish event) {
        if (!(event.getEntity() instanceof ServerPlayer player)) {
            return;
        }
        ItemStack stack = event.getItem();
        FoodProperties food = stack.m_41720_().m_41473_();
        if (food == null) {
            return;
        }
        FoodData data = player.m_36324_();
        float saturation = food.m_38744_() * food.m_38745_() * 2;
        double hearty = Perks.get(player, "hearty_meals");
        if (hearty > 0) {
            data.m_38717_((float) Math.min(data.m_38702_(), data.m_38722_() + saturation * hearty));
        }
        double feast = Perks.get(player, "harvest_feast");
        if (feast > 0 && tagged(stack, CROP_TAGS)) {
            data.m_38707_((int) Math.round(food.m_38744_() * feast), 0);
        }
        double sushi = Perks.get(player, "sushi_chef");
        if (sushi > 0 && tagged(stack, FISH_TAGS)) {
            player.m_7292_(new MobEffectInstance(MobEffects.f_19608_, (int) (600 * sushi), 0, false, true));
            data.m_38717_((float) Math.min(data.m_38702_(), data.m_38722_() + 2 * sushi));
        }
        double chef = Perks.get(player, "chef");
        if (chef > 0) {
            for (Pair<MobEffectInstance, Float> pair : food.m_38749_()) {
                MobEffectInstance active = player.m_21124_(pair.getFirst().m_19544_());
                if (active != null) {
                    player.m_7292_(new MobEffectInstance(active.m_19544_(), (int) (active.m_19557_() * (1 + chef)),
                            active.m_19564_(), active.m_19571_(), active.m_19572_()));
                }
            }
        }
        double picnic = Perks.get(player, "picnic");
        if (picnic > 0) {
            player.m_5634_((float) picnic);
            for (ServerPlayer friend : player.m_284548_().m_6907_()) {
                if (friend != player && friend.m_20280_(player) < 64
                        && Parties.same(player.m_20194_(), player.m_20148_(), friend.m_20148_())) {
                    friend.m_5634_((float) picnic);
                }
            }
        }
    }

    private static boolean tagged(ItemStack stack, Set<String> tags) {
        for (String tag : tags) {
            if (stack.m_204117_(TagKey.m_203882_(ForgeRegistries.Keys.ITEMS, new ResourceLocation(tag)))) {
                return true;
            }
        }
        return false;
    }
}
```

Names to verify with javap:

| SRG name | Member |
|---|---|
| `f_19608_` | MobEffects.WATER_BREATHING |
| `m_21124_` | getEffect |
| `m_19544_` | getEffect |
| `m_19557_` | getDuration |
| `m_19564_` | getAmplifier |
| `m_19571_` | isAmbient |
| `m_19572_` | isVisible |

```java
package fotfskills.mixin;

import fotfskills.perk.Perks;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.player.Player;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.ModifyVariable;

/** Trail Rations: hunger drain while sprinting is reduced. Player.causeFoodExhaustion = m_36399_. */
@Mixin(value = Player.class, remap = false)
public abstract class PlayerExhaustionMixin {
    @ModifyVariable(method = "m_36399_", at = @At("HEAD"), ordinal = 0, argsOnly = true, remap = false)
    private float fotfskills$trailRations(float exhaustion) {
        Player player = (Player) (Object) this;
        if (player instanceof ServerPlayer server && server.m_20142_()) {
            return (float) (exhaustion * (1 - Perks.get(server, "trail_rations")));
        }
        return exhaustion;
    }
}
```

- [ ] **Step 4: Write `FishingPerks`**

```java
package fotfskills.perk;

import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.OwnableEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.FishingHook;
import net.minecraft.world.entity.vehicle.Boat;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.phys.EntityHitResult;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.ProjectileImpactEvent;
import net.minecraftforge.event.entity.player.ItemFishedEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.items.ItemHandlerHelper;
import net.minecraftforge.registries.ForgeRegistries;

/** Hook Shot (the bobber hits mobs), Leviathan Bait (rare trophy fish), Sea Legs (faster boats, on the driver's client). */
public final class FishingPerks {
    @SubscribeEvent
    public void onHookHit(ProjectileImpactEvent event) {
        if (event.getProjectile() instanceof FishingHook hook && hook.m_37168_() instanceof ServerPlayer player
                && event.getRayTraceResult() instanceof EntityHitResult hit && hit.m_82443_() instanceof LivingEntity target
                && !(target instanceof Player) && !(target instanceof OwnableEntity owned && owned.m_21805_() != null)) {
            double shot = Perks.get(player, "hook_shot");
            if (shot > 0) {
                target.m_6469_(player.m_269291_().m_269075_(player), (float) shot);
                Vec3 pull = player.m_20182_().m_82546_(target.m_20182_()).m_82541_().m_82490_(0.4 * shot);
                target.m_5997_(pull.f_82479_, 0.2, pull.f_82481_);
            }
        }
    }

    @SubscribeEvent
    public void onFished(ItemFishedEvent event) {
        if (event.getEntity() instanceof ServerPlayer player && Perks.roll(player, "leviathan")) {
            ItemStack trophy = new ItemStack(ForgeRegistries.ITEMS.getValue(new ResourceLocation("minecraft", "tropical_fish")));
            trophy.m_41714_(Component.m_237113_("Leviathan Trophy"));
            trophy.m_41663_(net.minecraft.world.item.enchantment.Enchantments.f_44986_, 1);   // glint
            ItemHandlerHelper.giveItemToPlayer(player, trophy);
        }
    }

    /** Sea Legs: boats are driven client-side, so the driver's client scales the boat's speed (synced perk totals). */
    @SubscribeEvent
    public void onPlayerTick(TickEvent.PlayerTickEvent event) {
        Player player = event.player;
        if (event.phase != TickEvent.Phase.END || !player.m_9236_().f_46443_ || !(player.m_20202_() instanceof Boat boat)
                || boat.m_6688_() != player) {
            return;
        }
        double faster = Perks.get(player, "sea_legs");
        if (faster > 0 && boat.m_20069_()) {
            double f = Tuning.boatFactor(faster);
            Vec3 v = boat.m_20184_();
            boat.m_20256_(new Vec3(v.f_82479_ * f, v.f_82480_, v.f_82481_ * f));
        }
    }
}
```

Names to verify with javap:

| SRG name | Member |
|---|---|
| `m_82443_` | EntityHitResult.getEntity |
| `m_82546_` | Vec3.subtract |
| `m_82541_` | Vec3.normalize |
| `f_82479_` / `f_82480_` / `f_82481_` | Vec3.x / y / z |
| `f_44986_` | Enchantments.UNBREAKING |

Unbreaking is only there to make the trophy glint.

- [ ] **Step 5: Write `CraftPerks`**

```java
package fotfskills.perk;

import com.google.common.collect.Multimap;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.Attribute;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.inventory.AnvilMenu;
import net.minecraft.world.item.ArmorItem;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.EnchantedBookItem;
import net.minecraft.world.item.enchantment.Enchantment;
import net.minecraft.world.item.enchantment.EnchantmentHelper;
import net.minecraft.world.item.enchantment.EnchantmentInstance;
import net.minecraftforge.event.entity.player.AnvilRepairEvent;
import net.minecraftforge.event.entity.player.PlayerDestroyItemEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.items.ItemHandlerHelper;
import net.minecraftforge.registries.ForgeRegistries;

/**
 * Crafted gear (crafting grid): Enchanted Crafts I/II and Masterwork (guaranteed random enchantments), Smith (a
 * durability-saving chance stored on the item), Whetstone / Weaponsmith (+attack damage on weapons) and Armourer
 * (+toughness on armour), each applied once per item. Whetstone also applies to anvil repairs. Book Saver turns a
 * breaking enchanted tool into a book; Repair Kit refunds part of an anvil's XP cost.
 */
public final class CraftPerks {
    public static final String SMITH = "FotfSmith";
    private static final String STATS_DONE = "FotfStats";
    private static final String WHET_DONE = "FotfWhet";

    @SubscribeEvent
    public void onCraft(PlayerEvent.ItemCraftedEvent event) {
        if (event.getEntity() instanceof ServerPlayer player) {
            improve(player, event.getCrafting());
        }
    }

    /** Crafted gear only: damageable items. */
    public static void improve(ServerPlayer player, ItemStack stack) {
        if (stack.m_41619_() || !stack.m_41763_()) {
            return;
        }
        int cap = (int) Math.round(Perks.get(player, "enchant_level"));
        if (cap > 0) {
            int bonus = (int) Math.round(Perks.get(player, "enchant_bonus"));
            int count = Perks.get(player, "masterwork") > 0 ? 2 : 1;
            for (int i = 0; i < count; i++) {
                enchant(stack, cap, bonus);
            }
        }
        double smith = Perks.get(player, "smith");
        if (smith > 0) {
            stack.m_41784_().m_128350_(SMITH, (float) smith);
        }
        if (!stack.m_41784_().m_128441_(STATS_DONE)) {
            EquipmentSlot slot = LivingEntity.m_147233_(stack);
            double damage = Perks.get(player, "whetstone") + Perks.get(player, "weaponsmith");
            if (slot == EquipmentSlot.MAINHAND && damage > 0 && hasDefault(stack, slot, Attributes.f_22281_)) {
                addModifier(stack, slot, Attributes.f_22281_, damage);
                stack.m_41784_().m_128379_(STATS_DONE, true);
                stack.m_41784_().m_128379_(WHET_DONE, true);
            } else if (stack.m_41720_() instanceof ArmorItem && Perks.get(player, "armourer") > 0) {
                addModifier(stack, slot, Attributes.f_22285_, Perks.get(player, "armourer"));
                stack.m_41784_().m_128379_(STATS_DONE, true);
            }
        }
    }

    /** Whetstone on anvil repairs (once per item); Repair Kit refunds part of the anvil's level cost. */
    @SubscribeEvent
    public void onRepair(AnvilRepairEvent event) {
        if (!(event.getEntity() instanceof ServerPlayer player)) {
            return;
        }
        ItemStack out = event.getOutput();
        double whet = Perks.get(player, "whetstone");
        EquipmentSlot slot = LivingEntity.m_147233_(out);
        if (whet > 0 && out.m_41763_() && slot == EquipmentSlot.MAINHAND && !out.m_41784_().m_128441_(WHET_DONE)
                && hasDefault(out, slot, Attributes.f_22281_)) {
            addModifier(out, slot, Attributes.f_22281_, whet);
            out.m_41784_().m_128379_(WHET_DONE, true);
        }
        if (player.f_36096_ instanceof AnvilMenu anvil) {
            int refund = (int) Math.floor(anvil.m_39028_() * Perks.get(player, "repair_kit"));
            if (refund > 0) {
                player.m_6749_(refund);
            }
        }
    }

    @SubscribeEvent
    public void onBreak(PlayerDestroyItemEvent event) {
        if (!(event.getEntity() instanceof ServerPlayer player) || Perks.get(player, "book_saver") <= 0) {
            return;
        }
        Map<Enchantment, Integer> enchants = EnchantmentHelper.m_44831_(event.getOriginal());
        if (enchants.isEmpty()) {
            return;
        }
        ItemStack book = new ItemStack(Items.f_42690_);
        enchants.forEach((enchantment, level) -> EnchantedBookItem.m_41153_(book, new EnchantmentInstance(enchantment, level)));
        ItemHandlerHelper.giveItemToPlayer(player, book);
    }

    private static void enchant(ItemStack stack, int cap, int bonus) {
        Map<Enchantment, Integer> current = EnchantmentHelper.m_44831_(stack);
        List<Enchantment> options = new ArrayList<>();
        for (Enchantment e : ForgeRegistries.ENCHANTMENTS.getValues()) {
            if (e.m_6081_(stack) && !e.m_6589_() && !e.m_6591_() && !current.containsKey(e)
                    && current.keySet().stream().allMatch(other -> other.m_44695_(e))) {
                options.add(e);
            }
        }
        if (!options.isEmpty()) {
            Enchantment pick = options.get((int) (Perks.random() * options.size()));
            stack.m_41663_(pick, Tuning.enchantLevel(cap, bonus, pick.m_6586_(), Perks.random()));
        }
    }

    private static boolean hasDefault(ItemStack stack, EquipmentSlot slot, Attribute attribute) {
        return stack.m_41720_().m_7167_(slot).containsKey(attribute);
    }

    /** An NBT modifier turns off the item's default attributes, so the slot's defaults are copied in first. */
    private static void addModifier(ItemStack stack, EquipmentSlot slot, Attribute attribute, double amount) {
        CompoundTag tag = stack.m_41784_();
        if (!tag.m_128441_("AttributeModifiers")) {
            Multimap<Attribute, AttributeModifier> defaults = stack.m_41720_().m_7167_(slot);
            defaults.forEach((attr, modifier) -> stack.m_41643_(attr, modifier, slot));
        }
        stack.m_41643_(attribute, new AttributeModifier(UUID.randomUUID(), "fotfskills crafted", amount,
                AttributeModifier.Operation.ADDITION), slot);
    }
}
```

`m_128379_` is CompoundTag.putBoolean; verify it with javap. Note `Item.m_7167_` is vanilla's default per-slot map; Forge's stack-sensitive version isn't on the SRG classpath. A Ruling is needed only if behaviour differs.

- [ ] **Step 6: Wire it into existing code**
  - **`BlockPerks.onBroken`:** after the ore copies block and before `copies > 0`, add:

    ```java
    if (facts.hasTag("forge:ores") && !silk && Perks.roll(player, "autosmelt")) {
        autosmelt(level, pos);
    }
    if ((facts.hasTag("minecraft:base_stone_overworld")) && Perks.roll(player, "ore_nose")) {
        Block.m_49840_(level, pos, new ItemStack(ForgeRegistries.ITEMS.getValue(new ResourceLocation("minecraft",
                Perks.random() < 0.7 ? "iron_nugget" : "gold_nugget"))));
    }
    ```

    In the `matureCrop()` branch, add `FarmPerks.sweep(player, pos, state);`. Add the method:

    ```java
    /** Auto-smelt: this break's fresh drops at pos (spawned this tick) become their smelting result. */
    private static void autosmelt(ServerLevel level, BlockPos pos) {
        for (ItemEntity drop : level.m_45976_(ItemEntity.class, new AABB(pos).m_82400_(0.75))) {
            if (drop.f_19797_ != 0) {
                continue;
            }
            ItemStack stack = drop.m_32055_();
            level.m_7465_().m_44015_(RecipeType.f_44108_, new SimpleContainer(stack.m_41777_()), level).ifPresent(recipe -> {
                ItemStack result = recipe.m_8043_(level.m_9598_()).m_41777_();
                if (!result.m_41619_()) {
                    result.m_41764_(stack.m_41613_() * result.m_41613_());
                    drop.m_32045_(result);
                }
            });
        }
    }
    ```

    Imports needed: ItemEntity, AABB, RecipeType, SimpleContainer, ResourceLocation, ForgeRegistries.
  - **`ItemPerks.onCraft`:**
    - Food results (`result.m_41614_()`) also roll `cook_save`.
    - Results from `irons_spellbooks` or `ars_nouveau` also roll `spell_save`.
    - The existing `craft_save` roll becomes `Perks.random() < craft_save + (edible ? cook_save : 0) + (spell ? spell_save : 0)`.
  - **`ItemStackDurabilityMixin`:** after the pickaxe/armour chance, also save points with the item's `FotfSmith` float: `amount = Chance.reduce(amount, tag.getFloat(SMITH), Perks::random)` when the tag has it.
  - **`fotfskills.mixins.json`:** add `"PlayerExhaustionMixin"` to `mixins`.
  - **`FotfSkills`:** register `FarmPerks`, `FoodPerks`, `FishingPerks` and `CraftPerks`.

- [ ] **Step 7: Build and test.**
  - Run: `bash extras/fotfskills/test.sh && bash extras/fotfskills/build.sh`
  - Expected: all tests `ok`, `Built`.

- [ ] **Step 8: Commit**

```bash
git add extras/fotfskills
git commit -m "Skills 3c: farming, food, fishing and crafting perk hooks"
```

---

### Task 3: Wire the nodes

**Files:**
- Modify: `tools/skills/perks.json`, `tools/skills/test_make_skill_trees.py`

- [ ] **Step 1: Write the failing test**

```python
def test_crafting_cooking_farming_fishing_nodes_are_wired():
    expect = {('mining', 'smelter_1'): ('autosmelt', 0.12), ('farm', 'green_thumb_1'): ('green_thumb', 0.06),
              ('farm', 'sweeping_harvest_2'): ('sweeping_harvest', 1), ('cook', 'hearty_meals_1'): ('hearty_meals', 0.1),
              ('craft', 'enchanted_crafts_1'): ('enchant_level', 1), ('craft', 'masterwork_1'): ('masterwork', 1),
              ('fish', 'sea_legs_1'): ('sea_legs', 0.05), ('forage', 'berry_picker_1'): ('berry_picker', 0.1)}
    for (tree_id, sid), (perk, value) in expect.items():
        defs = g.build_category(tree(tree_id), TIERS, XP, PERKS)['definitions.json']
        assert {'type': 'fotfskills:perk', 'data': {'perk': perk, 'value': value}} in defs[sid]['rewards'], sid
    fish = g.build_category(tree('fish'), TIERS, XP, PERKS)['definitions.json']
    assert {'type': 'puffish_skills:attribute', 'data': {'attribute': 'minecraft:generic.luck', 'value': 1,
            'operation': 'addition'}} in fish['lucky_line_1']['rewards']
```

- [ ] **Step 2: Run.**
  - Run: `python -m pytest -q -p no:cacheprovider tools/skills`
  - Expected: FAIL.

- [ ] **Step 3: Add these entries to `perks.json`** (`P(id, v)`; `A(attr, v)` is an addition attribute)

**Mining**

| Node | Reward(s) |
|---|---|
| smelter | P(autosmelt, 0.12) |
| ore_nose | P(ore_nose, 0.03) |

**Forage**

| Node | Reward(s) |
|---|---|
| berry_picker | P(berry_picker, 0.1) |
| beekeeper | P(beekeeper, 0.2) |

**Farm**

| Node | Reward(s) |
|---|---|
| green_thumb | P(green_thumb, 0.06) |
| gardener | P(green_thumb, 0.06) + P(crop_drops, 0.02) |
| fertile_soil | P(fertile_soil, 0.08) |
| fertile_soil_ii | P(fertile_soil, 0.08) |
| harvest_feast | P(harvest_feast, 0.1) |
| sweeping_harvest | P(sweeping_harvest, 1) |
| compost_king | P(compost_king, 0.5) |

**Fish**

| Node | Reward(s) |
|---|---|
| lucky_line | A(minecraft:generic.luck, 1) |
| treasure_hunter | A(minecraft:generic.luck, 2) |
| leviathan_bait | P(leviathan, 0.02) |
| hook_shot | P(hook_shot, 1) |
| sushi_chef | P(sushi_chef, 1) |
| sea_legs | P(sea_legs, 0.05) |

**Cook**

| Node | Reward(s) |
|---|---|
| thrifty_cook | P(cook_save, 0.03) |
| thrifty_cook_ii | P(cook_save, 0.03) |
| hearty_meals | P(hearty_meals, 0.1) |
| chef | P(chef, 0.17) |
| trail_rations | P(trail_rations, 0.1) |
| picnic | P(picnic, 1) |

**Craft**

| Node | Reward(s) |
|---|---|
| smith | P(smith, 0.05) |
| whetstone | P(whetstone, 0.2) |
| enchanted_crafts | P(enchant_level, 1) |
| enchanted_crafts_ii | P(enchant_bonus, 1) |
| weaponsmith | P(weaponsmith, 1) |
| armourer | P(armourer, 1) |
| masterwork | P(masterwork, 1) |
| book_saver | P(book_saver, 1) |
| repair_kit | P(repair_kit, 0.15) |
| spellwright | P(spell_save, 0.08) |

- [ ] **Step 4: Run.**
  - Run: `python -m pytest -q -p no:cacheprovider tools/skills`
  - Expected: all passed (31).

- [ ] **Step 5: Commit**

```bash
python tools/skills/make_skill_trees.py
git add tools/skills config/puffish_skills
git commit -m "Skills 3c: crafting, cooking, farming and fishing nodes wired"
```

---

### Task 4: Pack and boot

- [ ] **Step 1:** Update the jar sha512 and run `packwiz refresh`. Commit `Skills 3c: ship rebuilt add-on`, push, and reboot the test server with `PACK_REF=<sha>`.
- [ ] **Step 2:** The boot log must show `Mod configuration loaded successfully!` with no fotfskills or mixin errors.
- [ ] **Step 3:** In-game rows go on the playtest list:
  - Enchanted Crafts enchants a crafted pickaxe.
  - Weaponsmith: the sword shows +1 damage and keeps its base damage.
  - Smelter: iron ore sometimes drops an iron ingot.
  - Sweeping Harvest reaps a 3x3 with a scythe.
  - Green Thumb: planted wheat sometimes starts taller.
  - Sea Legs: the boat is faster.
  - Hearty Meals: more saturation (shown by AppleSkin).
