# Skills Phase 4: Hearts, Grappling Hook, ParCool, Tree Reset, Pet Revival Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Finish the spec's remaining systems:
- Total-level hearts and stamina, which replace Paragliders. Paragliders is removed on this branch.
- A single grappling hook, upgraded by the Agility nodes Long Rope I/II, Hookmaster, Motor Reel and Twin Hooks. The other hooks and their upgrade items are removed from recipes and hidden in JEI.
- ParCool stamina nodes: Light Feet, Freerunner, Second Breath and Roll Master.
- Tree reset for XP levels.
- Standalone pet revival through a Pet Memento item, made cheaper by Soul Mender.
- A Skills entry in the FOTF Field Guide.

**Architecture:**
- **Pure rules**, unit-tested: `HeartCurve.steps(total)` and `ResetCost.levels(spent)`.
- **`TotalLevel`** recomputes every second per player. It sums the 12 skill levels and sets two transient modifiers: max health (+2 per step) and ParCool max stamina (+5% per step).
- **`GrapplePerks`** rewrites the `custom` NBT on every grappling hook in the player's inventory, using the mod's `GrappleCustomization` class, and only when the result changes. Its class is loaded only when `grapplemod` is present.
- **ParCool nodes** are plain attribute rewards on ParCool's own attributes.
- **`/fotfskills reset <tree>`** charges `max(5, ceil(spent / 2))` XP levels and calls Pufferfish's `Category.resetSkills`.
- **Pet Memento** is a registered item (`fotfskills:pet_memento`, fire-resistant, stacks to 1):
  - When an owned animal dies, a memento holding its full NBT drops at the death spot. It goes straight to the owner instead if they're online and far away (over 32 blocks, or in another dimension).
  - Using it on a block revives the pet there. That costs one golden apple from the inventory; Soul Mender gives a 25% chance per rank to keep the apple.

**Tech Stack:**
- Java 17 javac in Docker against SRG names.
- Forge 47.4.23 (DeferredRegister, events).
- Grappling Hook Reforged 1.2 API classes.
- ParCool attributes `parcool:parcool.max_stamina`, `parcool:parcool.stamina_recovery`, `parcool:parcool.breakfall.damage_reduction`.
- KubeJS 6 recipe removal and JEI hiding.
- packwiz.
- Python generator + pytest.

**Spec:** `docs/superpowers/specs/2026-10-03-skills-design.md`. Relevant parts:
- Rev 3: "Grappling hook ...", "Paragliders is removed", "Tree reset".
- Rev 4/5: "Overall level hearts follow a gentle curve ... 8, 19, 32, 46, 61, 78, 95, 113, 132, 151, 171, 192, 213, 234, 256".
- "Pet revival (standalone, not a perk)".

## Global Constraints

- Hearts: each step gives +1 heart (2 health) and +5% ParCool max stamina. All 15 steps are reached at total level 256. The thresholds are exactly the spec's list.
- Tree reset costs 1 XP level per 2 points spent, minimum 5. Any player can use it; Pufferfish's own reset needs op.
- Pet revival works without Pufferfish. Soul Mender only makes it cheaper.
- No duplication:
  - A memento is created once per death.
  - Reviving consumes the memento.
  - A revived pet keeps its UUID, so a second copy can't exist.
- Paragliders removal happens only on `skills-preview`. It reaches the live server only when Dylan approves the release merge.
- Perk ids live in `Perks.CAPS`. Node ids keep `<slug>_<k>`. Pufferfish stays pinned at 0.19.1.

## Decisions taken without Dylan (listed for him at the end)

- **Revival cost:** one golden apple, used instantly. The spec left the exact cost open.
- **Light Feet and Freerunner:** "less stamina drain" is done as more max stamina (5% per rank, and 8% per rank) through ParCool's attribute. ParCool has no drain multiplier.
- **Grappling hook values:**
  - Long Rope adds 4 blocks per rank to the 30-block rope, capped at the config's 60.
  - Hookmaster adds +15% throw speed and swing control per rank.
  - Motor Reel turns the motor on, +25% motor speed per rank after the first.
  - Twin Hooks turns on the double hook.
- **Existing hooks and upgrade items** already in inventories stay usable. Only recipes are removed, and the items are hidden in JEI.

## Review Focus

1. **Pet Memento duplication.** Death events firing twice, a pet killed while riding, or a memento revived inside a block.
2. **Hearts modifier.** It stays after relog (it's re-applied within 1 second), never kills when it lowers, and includes nothing when Pufferfish has no data.
3. **GrapplePerks** touches only `GrapplehookItem` stacks, writes only on change, and never runs where grapplemod is missing.
4. **Reset** can't run with too few levels, and charges by spent points before the reset.
5. **Paragliders removal** leaves no dangling references: keybinding defaults, guide icons, KubeJS.

---

### Task 1: Pure rules

**Files:**
- Create: `extras/fotfskills/src/fotfskills/perk/HeartCurve.java`, `ResetCost.java`
- Create: `extras/fotfskills/test/fotfskills/perk/Phase4LogicTest.java`

- [ ] **Step 1: Write the failing test.**

```java
package fotfskills.perk;

/** Total-level hearts and tree reset cost. Run: sh test.sh */
public final class Phase4LogicTest {
    public static void main(String[] args) {
        check(HeartCurve.steps(0) == 0 && HeartCurve.steps(7) == 0, "no hearts before total level 8");
        check(HeartCurve.steps(8) == 1 && HeartCurve.steps(18) == 1 && HeartCurve.steps(19) == 2, "spec thresholds");
        check(HeartCurve.steps(255) == 14 && HeartCurve.steps(256) == 15 && HeartCurve.steps(600) == 15, "15 hearts by 256");
        check(ResetCost.levels(0) == 5 && ResetCost.levels(9) == 5 && ResetCost.levels(11) == 6, "1 per 2 points, minimum 5");
        check(ResetCost.levels(50) == 25, "a full tree costs 25 levels");
        System.out.println("Phase4LogicTest ok");
    }

    private static void check(boolean ok, String what) {
        if (!ok) { System.out.println("FAIL: " + what); System.exit(1); }
    }
}
```

- [ ] **Step 2: Run it.**
  - Run: `bash extras/fotfskills/test.sh`
  - Expected: `cannot find symbol: class HeartCurve`.

- [ ] **Step 3: Implement.**

```java
package fotfskills.perk;

/** Spec rev 5: heart step k of 15 needs 256 x (k/15)^1.3 total skill levels. */
public final class HeartCurve {
    public static final int[] THRESHOLDS = {8, 19, 32, 46, 61, 78, 95, 113, 132, 151, 171, 192, 213, 234, 256};

    private HeartCurve() {
    }

    public static int steps(int totalLevel) {
        int steps = 0;
        for (int threshold : THRESHOLDS) {
            if (totalLevel >= threshold) {
                steps++;
            }
        }
        return steps;
    }
}
```

```java
package fotfskills.perk;

/** Resetting a tree costs 1 XP level per 2 points spent in it, at least 5. */
public final class ResetCost {
    private ResetCost() {
    }

    public static int levels(int spentPoints) {
        return Math.max(5, (spentPoints + 1) / 2);
    }
}
```

- [ ] **Step 4: Run.**
  - Run: `bash extras/fotfskills/test.sh`
  - Expected: `Phase4LogicTest ok` plus the earlier tests.

- [ ] **Step 5: Commit** `Skills 4: heart curve and reset cost`.

---

### Task 2: Hearts, grappling hook, reset command

**Files:**
- Create: `extras/fotfskills/src/fotfskills/perk/TotalLevel.java`, `GrapplePerks.java`
- Modify: `FotfCommands.java` (reset), `ConditionalStats.java` (total level line), `Perks.java` (ids), `FotfSkills.java`

- [ ] **Step 1: Add these entries to `Perks.CAPS`:**

```java
            Map.entry("hook_range", 30.0), Map.entry("hook_speed", 2.0), Map.entry("hook_motor", 10.0),
            Map.entry("hook_double", 1.0), Map.entry("soul_mender", 1.0)
```

- [ ] **Step 2: Write `TotalLevel`.**

```java
package fotfskills.perk;

import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.registries.ForgeRegistries;
import net.puffish.skillsmod.api.SkillsAPI;

/**
 * Overall level (all 12 skill levels added up) replaces Paragliders' heart containers and stamina vessels: every step of
 * HeartCurve gives +1 heart and +5% ParCool max stamina. Refreshed every second as transient modifiers.
 */
public final class TotalLevel {
    private static final Map<UUID, Integer> TOTALS = new ConcurrentHashMap<>();

    public static int get(UUID player) {
        return TOTALS.getOrDefault(player, 0);
    }

    @SubscribeEvent
    public void onTick(TickEvent.PlayerTickEvent event) {
        if (event.phase != TickEvent.Phase.END || !(event.player instanceof ServerPlayer player) || player.f_19797_ % 20 != 5) {
            return;
        }
        int total = SkillsAPI.streamCategories()
                .mapToInt(category -> category.getExperience().map(e -> e.getLevel(player)).orElse(0)).sum();
        TOTALS.put(player.m_20148_(), total);
        int steps = HeartCurve.steps(total);
        Modifiers.set(player, Attributes.f_22276_, "total_hearts", 2.0 * steps, AttributeModifier.Operation.ADDITION);
        Modifiers.set(player, ForgeRegistries.ATTRIBUTES.getValue(new ResourceLocation("parcool", "parcool.max_stamina")),
                "total_stamina", 0.05 * steps, AttributeModifier.Operation.MULTIPLY_BASE);
    }
}
```

- [ ] **Step 3: Write `GrapplePerks`.** Register it only when `ModList.get().isLoaded("grapplemod")`.

```java
package fotfskills.perk;

import com.yyon.grapplinghook.items.GrapplehookItem;
import com.yyon.grapplinghook.utils.GrappleCustomization;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;

/**
 * The single grappling hook is upgraded by Agility nodes instead of upgrade items: every second, each hook in the
 * player's inventory gets the customization their perks give (Long Rope: rope length; Hookmaster: throw speed and swing
 * control; Motor Reel: motor; Twin Hooks: double hook). Written only when it changes.
 */
public final class GrapplePerks {
    private static final double BASE_ROPE = 30;
    private static final double MAX_ROPE = 60;

    @SubscribeEvent
    public void onTick(TickEvent.PlayerTickEvent event) {
        if (event.phase != TickEvent.Phase.END || !(event.player instanceof ServerPlayer player) || player.f_19797_ % 20 != 10) {
            return;
        }
        for (ItemStack stack : player.m_150109_().f_35974_) {
            if (stack.m_41720_() instanceof GrapplehookItem hook) {
                GrappleCustomization wanted = customization(player);
                if (hook.getCustomization(stack).getChecksum() != wanted.getChecksum()) {
                    hook.setCustomOnServer(stack, wanted, player);
                }
            }
        }
    }

    private static GrappleCustomization customization(ServerPlayer player) {
        GrappleCustomization c = new GrappleCustomization();
        c.maxlen = Math.min(MAX_ROPE, BASE_ROPE + Perks.get(player, "hook_range"));
        double speed = Perks.get(player, "hook_speed");
        c.throwspeed *= 1 + speed;
        c.playermovementmult *= 1 + speed;
        double motor = Perks.get(player, "hook_motor");
        if (motor > 0) {
            c.motor = true;
            c.motormaxspeed *= 1 + 0.25 * (motor - 1);
        }
        if (Perks.get(player, "hook_double") > 0) {
            c.doublehook = true;
        }
        return c;
    }
}
```

- [ ] **Step 4: Add the reset command.** In `FotfCommands.onRegister`, add this branch:

```java
                .then(Commands.m_82127_("reset")
                        .then(Commands.m_82129_("tree", com.mojang.brigadier.arguments.StringArgumentType.word())
                                .suggests((ctx, builder) -> {
                                    SkillsAPI.streamCategories().forEach(c -> builder.suggest(c.getId().m_135815_()));
                                    return builder.buildFuture();
                                })
                                .executes(FotfCommands::reset)))
```

Then add the method:

```java
    /** Gives back every point in one tree for 1 XP level per 2 points spent (at least 5). */
    private static int reset(CommandContext<CommandSourceStack> ctx) throws com.mojang.brigadier.exceptions.CommandSyntaxException {
        ServerPlayer player = ctx.getSource().m_81375_();
        String tree = com.mojang.brigadier.arguments.StringArgumentType.getString(ctx, "tree");
        Category category = SkillsAPI.streamCategories().filter(c -> c.getId().m_135815_().equals(tree)).findFirst().orElse(null);
        if (category == null) {
            ctx.getSource().m_288197_(() -> Component.m_237113_("§cNo skill tree called " + tree + "."), false);
            return 0;
        }
        int spent = category.getSpentPoints(player);
        int cost = ResetCost.levels(spent);
        if (spent == 0) {
            ctx.getSource().m_288197_(() -> Component.m_237113_("You haven't spent any points in " + tree + "."), false);
            return 0;
        }
        if (player.f_36078_ < cost) {
            ctx.getSource().m_288197_(() -> Component.m_237113_("§cResetting " + tree + " costs " + cost
                    + " XP levels (1 per 2 points spent, at least 5). You have " + player.f_36078_ + "."), false);
            return 0;
        }
        player.m_6749_(-cost);
        category.resetSkills(player);
        ctx.getSource().m_288197_(() -> Component.m_237113_("§6" + tree + "§f reset: " + spent
                + " points back for " + cost + " XP levels."), false);
        return 1;
    }
```

Imports: `net.puffish.skillsmod.api.Category` and `net.puffish.skillsmod.api.SkillsAPI`.

- [ ] **Step 5: Show the total level in the buff list.** In `ConditionalStats`, before the labels-changed check, add:

```java
        int total = TotalLevel.get(player.m_20148_());
        if (total > 0) {
            labels.add(0, "Total level " + total + " (+" + HeartCurve.steps(total) + " hearts)");
        }
```

- [ ] **Step 6: Register and build.**
  - Register `new TotalLevel()` in `FotfSkills`, and register `new GrapplePerks()` behind the grapplemod check.
  - Run: `bash extras/fotfskills/test.sh && bash extras/fotfskills/build.sh`
  - Expected: all tests `ok`, `Built`.

- [ ] **Step 7: Commit** `Skills 4: total-level hearts and stamina, grappling hook upgrades, tree reset`.

---

### Task 3: Pet Memento

**Files:**
- Create: `extras/fotfskills/src/fotfskills/pet/ModItems.java`, `PetMementoItem.java`, `PetMementos.java`
- Create: `extras/fotfskills/res/assets/fotfskills/models/item/pet_memento.json`, `extras/fotfskills/res/assets/fotfskills/lang/en_us.json`, `extras/fotfskills/draw_memento.py` (writes `res/assets/fotfskills/textures/item/pet_memento.png`)
- Modify: `FotfSkills.java` (register the items on the mod bus and `PetMementos` on the Forge bus)

- [ ] **Step 1: `ModItems`.**

```java
package fotfskills.pet;

import net.minecraft.world.item.Item;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

/** The add-on's items. */
public final class ModItems {
    private static final DeferredRegister<Item> ITEMS = DeferredRegister.create(ForgeRegistries.ITEMS, "fotfskills");
    public static final RegistryObject<Item> PET_MEMENTO = ITEMS.register("pet_memento",
            () -> new PetMementoItem(new Item.Properties().m_41487_(1).m_41486_()));

    private ModItems() {
    }

    public static void register(IEventBus modBus) {
        ITEMS.register(modBus);
    }
}
```

- [ ] **Step 2: `PetMementoItem`.**

```java
package fotfskills.pet;

import fotfskills.perk.Perks;
import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.context.UseOnContext;
import net.minecraft.world.level.Level;

/**
 * Holds a fallen pet (its whole saved data). Using it on a block brings the pet back there, healed, for one golden
 * apple from your inventory; Taming's Soul Mender gives a 25% chance per rank to keep the apple.
 */
public final class PetMementoItem extends Item {
    public static final String PET = "FotfPet";
    public static final String NAME = "FotfPetName";

    public PetMementoItem(Properties properties) {
        super(properties);
    }

    @Override
    public InteractionResult m_6225_(UseOnContext context) {
        ItemStack memento = context.m_43722_();
        if (!(context.m_43725_() instanceof ServerLevel level) || !(context.m_43723_() instanceof ServerPlayer player)) {
            return InteractionResult.SUCCESS;
        }
        CompoundTag tag = memento.m_41783_();
        if (tag == null || !tag.m_128441_(PET)) {
            return InteractionResult.FAIL;
        }
        int apple = findApple(player);
        if (apple < 0 && !player.m_7500_()) {
            player.m_5661_(Component.m_237113_("§cYou need a golden apple to revive " + tag.m_128461_(NAME) + "."), true);
            return InteractionResult.FAIL;
        }
        BlockPos at = context.m_8083_().m_121945_(context.m_43719_());
        CompoundTag data = tag.m_128469_(PET).m_6426_();
        data.m_128473_("DeathTime");
        data.m_128473_("HurtTime");
        Entity pet = EntityType.m_20642_(data, level).orElse(null);
        if (pet == null) {
            return InteractionResult.FAIL;
        }
        pet.m_7678_(at.m_123341_() + 0.5, at.m_123342_(), at.m_123343_() + 0.5, pet.m_146908_(), 0);
        if (pet instanceof LivingEntity living) {
            living.m_21153_(living.m_21233_());
        }
        if (level.m_8791_(pet.m_20148_()) != null) {
            player.m_5661_(Component.m_237113_("§c" + tag.m_128461_(NAME) + " is already alive."), true);
            return InteractionResult.FAIL;
        }
        level.m_7967_(pet);
        if (apple >= 0 && !player.m_7500_() && !Perks.roll(player, "soul_mender")) {
            player.m_150109_().f_35974_.get(apple).m_41774_(1);
        }
        if (!player.m_7500_()) {
            memento.m_41774_(1);
        }
        level.m_8767_(ParticleTypes.f_123750_, pet.m_20185_(), pet.m_20186_() + 1, pet.m_20189_(), 12, 0.5, 0.5, 0.5, 0.1);
        level.m_5594_(null, at, SoundEvents.f_12275_, SoundSource.PLAYERS, 1.0f, 1.2f);
        player.m_5661_(Component.m_237113_("§a" + tag.m_128461_(NAME) + " is back!"), true);
        return InteractionResult.CONSUME;
    }

    private static int findApple(ServerPlayer player) {
        List<ItemStack> items = player.m_150109_().f_35974_;
        for (int i = 0; i < items.size(); i++) {
            if (items.get(i).m_150930_(Items.f_42436_)) {
                return i;
            }
        }
        return -1;
    }

    @Override
    public void m_7373_(ItemStack stack, Level level, List<Component> tooltip, TooltipFlag flag) {
        CompoundTag tag = stack.m_41783_();
        if (tag != null && tag.m_128441_(NAME)) {
            tooltip.add(Component.m_237113_("§d" + tag.m_128461_(NAME)));
        }
        tooltip.add(Component.m_237113_("§7Use on a block with a golden apple in your inventory to bring your pet back."));
    }
}
```

Names to verify with javap:

| SRG name | Member |
|---|---|
| `m_128461_` | getString |
| `m_128469_` | getCompound |
| `m_128473_` | remove |
| `m_123341_` / `m_123342_` / `m_123343_` | getX / getY / getZ |
| `m_8791_` | ServerLevel.getEntity(UUID) |
| `m_8767_` | sendParticles |
| `m_5594_` | playSound with a null player |

- [ ] **Step 3: `PetMementos` (on death).**

```java
package fotfskills.pet;

import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.OwnableEntity;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.event.entity.living.LivingDeathEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.items.ItemHandlerHelper;

/** A tamed animal or companion that dies leaves a Pet Memento: at its death spot, or with its owner if they're far away. */
public final class PetMementos {
    @SubscribeEvent(priority = EventPriority.LOWEST)
    public void onDeath(LivingDeathEvent event) {
        LivingEntity pet = event.getEntity();
        if (event.isCanceled() || pet.m_9236_().f_46443_ || pet instanceof Player
                || !(pet instanceof OwnableEntity owned) || owned.m_21805_() == null) {
            return;
        }
        CompoundTag data = new CompoundTag();
        if (!pet.m_20086_(data)) {
            return;                       // passengers and entities that can't be saved
        }
        ItemStack memento = new ItemStack(ModItems.PET_MEMENTO.get());
        memento.m_41784_().m_128365_(PetMementoItem.PET, data);
        memento.m_41784_().m_128359_(PetMementoItem.NAME, pet.m_5446_().getString());
        if (owned.m_269323_() instanceof ServerPlayer owner
                && (owner.m_9236_() != pet.m_9236_() || owner.m_20280_(pet) > 32 * 32)) {
            ItemHandlerHelper.giveItemToPlayer(owner, memento);
            return;
        }
        ItemEntity drop = new ItemEntity(pet.m_9236_(), pet.m_20185_(), pet.m_20186_() + 0.5, pet.m_20189_(), memento);
        drop.m_32064_();
        pet.m_9236_().m_7967_(drop);
    }
}
```

`m_128359_` is putString; verify it with javap.

- [ ] **Step 4: Assets.**
  - Model: `{"parent": "minecraft:item/generated", "textures": {"layer0": "fotfskills:item/pet_memento"}}`.
  - Lang: `{"item.fotfskills.pet_memento": "Pet Memento"}`.
  - `draw_memento.py` draws a 16x16 locket: a gold ring with a pink heart, outlined, written with PIL to `res/assets/fotfskills/textures/item/pet_memento.png`.

- [ ] **Step 5: Register.** In the `FotfSkills` constructor:
  - `ModItems.register(net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext.get().getModEventBus())`
  - `MinecraftForge.EVENT_BUS.register(new PetMementos())`

- [ ] **Step 6: Build.**
  - Run: `python extras/fotfskills/draw_memento.py && bash extras/fotfskills/test.sh && bash extras/fotfskills/build.sh`
  - Expected: all `ok`, `Built`.

- [ ] **Step 7: Commit** `Skills 4: Pet Memento revival`.

---

### Task 4: Nodes, pack changes, guide

**Files:**
- Modify: `tools/skills/perks.json`, `tools/skills/test_make_skill_trees.py`
- Create: `kubejs/server_scripts/single_grappling_hook.js`, `kubejs/client_scripts/single_grappling_hook.js`
- Remove: `mods/paragliders.pw.toml` (`packwiz remove paragliders`)
- Modify:
  - `config/defaultoptions/keybindings.txt` (drop the Paragliders key)
  - `patchouli_books/fotf_field_guide/en_us/categories/travel.json`
  - `patchouli_books/fotf_field_guide/en_us/entries/travel/gliding.json`
- Create: `patchouli_books/fotf_field_guide/en_us/entries/getting_started/skills.json`

- [ ] **Step 1: Write the failing test.**

```python
def test_phase4_nodes_are_wired():
    expect = {('agility', 'long_rope_1'): ('hook_range', 4), ('agility', 'long_rope_ii_1'): ('hook_range', 4),
              ('agility', 'hookmaster_1'): ('hook_speed', 0.15), ('agility', 'motor_reel_1'): ('hook_motor', 1),
              ('agility', 'twin_hooks_1'): ('hook_double', 1), ('taming', 'soul_mender_1'): ('soul_mender', 0.25)}
    for (tree_id, sid), (perk, value) in expect.items():
        defs = g.build_category(tree(tree_id), TIERS, XP, PERKS)['definitions.json']
        assert {'type': 'fotfskills:perk', 'data': {'perk': perk, 'value': value}} in defs[sid]['rewards'], sid
    agility = g.build_category(tree('agility'), TIERS, XP, PERKS)['definitions.json']
    assert {'type': 'puffish_skills:attribute', 'data': {'attribute': 'parcool:parcool.max_stamina', 'value': 0.05,
            'operation': 'multiply_base'}} in agility['light_feet_1']['rewards']
    assert agility['second_breath_1']['rewards'][0]['data']['attribute'] == 'parcool:parcool.stamina_recovery'
    assert agility['roll_master_1']['rewards'][0]['data']['attribute'] == 'parcool:parcool.breakfall.damage_reduction'
```

- [ ] **Step 2: Run it.** pytest is expected to FAIL.

- [ ] **Step 3: Add these entries to `perks.json`.**

**Agility**

| Node | Reward(s) |
|---|---|
| long_rope | P(hook_range, 4) |
| long_rope_ii | P(hook_range, 4) |
| hookmaster | P(hook_speed, 0.15) |
| motor_reel | P(hook_motor, 1) |
| twin_hooks | P(hook_double, 1) |
| light_feet | A(parcool:parcool.max_stamina, 0.05, multiply_base) |
| freerunner | A(parcool:parcool.max_stamina, 0.08, multiply_base) |
| second_breath | A(parcool:parcool.stamina_recovery, 0.1, multiply_base) |
| roll_master | A(parcool:parcool.breakfall.damage_reduction, 0.1, addition) |

**Taming**

| Node | Reward(s) |
|---|---|
| soul_mender | P(soul_mender, 0.25) |

- [ ] **Step 4: Run.** All tests pass. Regenerate the config.

- [ ] **Step 5: Single grappling hook (KubeJS).**
  - The server script removes recipes for every grapplemod item except `grapplemod:grapplinghook`:
    - the hooks: `motorhook`, `doublemotorhook`, `smarthook`, `enderhook`, `magnethook`, `rockethook`, `rocketdoublemotorhook`
    - the other gear: `launcheritem`, `repeller`, `longfallboots`, `doublejumpboots`, `wallrunboots`
    - every `*upgradeitem`, and `block_grapple_modifier`
  - The client script hides the same items in JEI (`JEIEvents.hideItems`).

- [ ] **Step 6: Paragliders out.**
  - Run `packwiz remove paragliders`.
  - Delete the `key_key.paraglider.*` line from the default keybindings.
  - Travel category: icon becomes `minecraft:elytra`, and the description becomes "Parkour, grappling hooks, airships and boats."
  - `gliding.json`: keep only the elytra page, renamed "Elytra", with the elytra icon.

- [ ] **Step 7: Field guide Skills entry** (`entries/getting_started/skills.json`). These pages explain:
  - how skills level, plus the skill menu key (Pufferfish default `K`)
  - tiers and points, and choice tiers
  - level-up messages and `/fotfskills levelups off`
  - `/fotfskills perks`, and the active buffs beside the inventory
  - total-level hearts (they replace gliders' heart containers)
  - `/fotfskills reset <tree>` and its cost
  - the Pet Memento
  - that the grappling hook upgrades come from Agility

- [ ] **Step 8: Refresh, commit, push, boot.**
  - Run `packwiz refresh`, commit `Skills 4: hook, ParCool and Soul Mender nodes; Paragliders removed; field guide`, push, and boot the test server.
  - Check: config loaded, no fotfskills, mixin or registry errors, and KubeJS shows 0 errors (`kubejs errors` / log).
