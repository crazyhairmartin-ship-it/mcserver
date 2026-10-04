# Skills Phase 2b: Common Perks Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the common perk nodes work: chance to save resources (durability, ingredients, ammo, treats, mana), extra output (ore/log/crop/wild drops, double catch, extra servings, animal drops), and activity boosts (mining/chopping speed, draw speed, bite time, fall damage, fire/blast wards, simple damage bonuses). Player-placed blocks give no gathering XP or extra drops.

**Architecture:** The add-on registers a `fotfskills:perk` reward (`{"perk": "<id>", "value": x}`). Pufferfish calls `update` per player. `Perks` keeps each player's per-perk totals, summed over unlocked ranks and capped per perk. Event handlers and three small mixins read those totals. Totals are synced to the client in one small packet so client-side break speed matches the server.

A per-dimension `PlacedBlocks` saved-data set marks player-placed gathering blocks. The new `fotfskills:break` XP source replaces the built-in `mine_block`/`break_block` sources for Mining, Foraging and Farming, so placed blocks give nothing. Mature crops are recognised generically (`CropBlock.isMaxAge`, or the `age` property at its max for anything in `#minecraft:crops`). The generator maps nodes to perks through `perks.json`.

**Tech Stack:** Python 3.12 + pytest (generator, perk/XP data). Java 17 javac in Docker against SRG names (`extras/fotfskills/build.sh`, `test.sh`). Pufferfish's Skills 0.19.1 API. Forge 47.4.23 events + SimpleChannel. Mixins (remap=false).

**Spec:** `docs/superpowers/specs/2026-10-03-skills-design.md` ("Perk types": saving resources, extra output, activity boosts; "Anti-farming"; "Risks": extra drops must not double with Fortune)

## Global Constraints

- Perks of the same type add up (ranks and nodes), with a per-type cap (spec).
- "Extra drops" never stack with Fortune or Silk Touch on the same ore (spec risk line). Placed blocks give no extra drops and no gathering XP.
- No duplication loops. Ingredient refunds need at least 2 different items in the grid (blocks un-crafting and compression give nothing). Ammo saving only refunds `#minecraft:arrows` and makes the fired arrow un-pickable.
- Bonuses are opt-in power only; nothing makes the world harder.
- Node ids keep the `<slug>_<k>` scheme. Pufferfish stays pinned at 0.19.1.
- Client-only code stays in the mixin `"client"` list. Packet handlers must not load client classes on the server.
- After each add-on build, update the sha512 in `mods/fotfskills.pw.toml` and run `packwiz refresh`. Boot the test server with `PACK_REF=<pushed sha>`.

## Review Focus

1. **Dupes.**
   - craft_free/craft_save with compress/decompress recipes.
   - ammo_save on tridents or modded thrown weapons that extend AbstractArrow.
   - extra drops on Silk Touch.
   - treat_saver when the stack runs out.

   Expected: none give net items except by the perk's intended chance on a normal craft or shot.
2. **Cancelled breaks.** A claim mod (Open Parties and Claims) cancelling BreakEvent must not still pay XP or extra drops. The handler runs at LOWEST priority and skips cancelled events.
3. **Client/server mismatch.** Break speed must be applied on the client too (perk sync), or mining looks slow while the server allows it faster. Every other perk is server-only.
4. **Missing mods.** Iron's/Ars perk listeners load only when the mod is present.
5. **Saved data growth.** PlacedBlocks only stores blocks in the tracked tags. Broken blocks are removed. The set survives restarts.

---

### Task 1: Perk reward, totals and client sync

**Files:**
- Create: `extras/fotfskills/src/fotfskills/perk/PerkTotals.java`, `Perks.java`, `PerkReward.java`, `Chance.java`, `PerkSync.java`, `ClientPerks.java`
- Create: `extras/fotfskills/test/fotfskills/perk/PerkLogicTest.java`
- Modify: `extras/fotfskills/test.sh` (compile all `src` + `test`, run every `*Test` class)
- Modify: `extras/fotfskills/src/fotfskills/FotfSkills.java`

**Interfaces:**
- Produces:
  - `Perks.get(Player, String perk) -> double` (capped total; on the client it reads the synced totals).
  - `Perks.roll(Player, String perk) -> boolean`.
  - `Perks.CAPS` (perk id to cap; Task 4 tests read the ids from this file).
  - `Chance.reduce(int amount, double chance, DoubleSupplier rnd) -> int` (amount minus saved points).
  - `Chance.successes(int count, double chance, DoubleSupplier rnd) -> int`.
  - Reward type `fotfskills:perk`, data `{"perk": String, "value": number}`. Unknown perk ids fail config load.

- [ ] **Step 1: Write the failing test**

`extras/fotfskills/test/fotfskills/perk/PerkLogicTest.java`:

```java
package fotfskills.perk;

import java.util.UUID;

/** Plain-java test of the perk bookkeeping (no game classes). Run: sh test.sh */
public final class PerkLogicTest {
    public static void main(String[] args) {
        PerkTotals totals = new PerkTotals(id -> id.equals("ore_drops") ? 0.10 : Double.MAX_VALUE);
        UUID a = UUID.randomUUID();
        Object rank1 = new Object(), rank2 = new Object(), rank3 = new Object();
        totals.put(a, rank1, "ore_drops", 0.03);
        totals.put(a, rank2, "ore_drops", 0.03);
        check(close(totals.total(a, "ore_drops"), 0.06), "ranks add up");
        totals.put(a, rank3, "ore_drops", 0.06);
        check(close(totals.total(a, "ore_drops"), 0.10), "capped at 0.10");
        totals.put(a, rank3, "ore_drops", 0);
        check(close(totals.total(a, "ore_drops"), 0.06), "a locked rank (value 0) drops out");
        totals.removeSource(rank2);
        check(close(totals.total(a, "ore_drops"), 0.03), "a disposed reward drops out");
        check(totals.total(a, "mining_speed") == 0, "untouched perk is 0");
        check(totals.snapshot(a).get("ore_drops") != null, "snapshot lists active perks");
        totals.removePlayer(a);
        check(totals.total(a, "ore_drops") == 0, "logout clears");

        check(Chance.reduce(10, 0, () -> 0.0) == 10, "no chance keeps all damage");
        check(Chance.reduce(10, 0.5, seq(0.1, 0.9)) == 5, "half the points saved");
        check(Chance.successes(4, 0.25, seq(0.1, 0.5, 0.9, 0.2)) == 2, "two of four rolls under 0.25");
        check(Refund.eligible(java.util.List.of("minecraft:iron_ingot", "minecraft:iron_ingot")) == false,
                "compression (one item type) is not refundable");
        check(Refund.eligible(java.util.List.of("minecraft:stick", "minecraft:iron_ingot")), "two item types refundable");
        check(!Refund.eligible(java.util.List.of("minecraft:oak_log")), "single-slot un-crafting not refundable");
        System.out.println("PerkLogicTest ok");
    }

    private static java.util.function.DoubleSupplier seq(double... values) {
        int[] i = {0};
        return () -> values[i[0]++ % values.length];
    }

    private static boolean close(double x, double y) {
        return Math.abs(x - y) < 1e-9;
    }

    private static void check(boolean ok, String what) {
        if (!ok) { System.out.println("FAIL: " + what); System.exit(1); }
    }
}
```

Change the last two lines of the `sh -c` block in `extras/fotfskills/test.sh` to:

```bash
    javac --release 17 -proc:none -nowarn -cp "$CP" -d /tmp/t $(find src test -name "*.java")
    for t in $(cd test && find . -name "*Test.java" | sed "s|^\./||; s|\.java$||; s|/|.|g"); do java -cp "/tmp/t:$CP" "$t"; done
```

- [ ] **Step 2: Run to verify it fails**

Run: `bash extras/fotfskills/test.sh`
Expected: FAIL with javac `cannot find symbol: class PerkTotals` (and `Chance`, `Refund`).

- [ ] **Step 3: Implement**

`src/fotfskills/perk/PerkTotals.java`:

```java
package fotfskills.perk;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import java.util.function.ToDoubleFunction;

/** Per-player perk totals: each unlocked reward (source) contributes a value to one perk; totals are capped. */
public final class PerkTotals {
    private record Part(String perk, double value) {
    }

    private final Map<UUID, Map<Object, Part>> parts = new HashMap<>();
    private final ToDoubleFunction<String> caps;

    public PerkTotals(ToDoubleFunction<String> caps) {
        this.caps = caps;
    }

    public synchronized void put(UUID player, Object source, String perk, double value) {
        Map<Object, Part> map = parts.computeIfAbsent(player, id -> new HashMap<>());
        if (value == 0) {
            map.remove(source);
        } else {
            map.put(source, new Part(perk, value));
        }
    }

    public synchronized void removeSource(Object source) {
        parts.values().forEach(map -> map.remove(source));
    }

    public synchronized void removePlayer(UUID player) {
        parts.remove(player);
    }

    public synchronized double total(UUID player, String perk) {
        double sum = 0;
        for (Part part : parts.getOrDefault(player, Map.of()).values()) {
            if (part.perk.equals(perk)) {
                sum += part.value;
            }
        }
        return Math.min(sum, caps.applyAsDouble(perk));
    }

    /** Every active perk's capped total, for syncing to the client. */
    public synchronized Map<String, Double> snapshot(UUID player) {
        Map<String, Double> out = new HashMap<>();
        for (Part part : parts.getOrDefault(player, Map.of()).values()) {
            out.merge(part.perk, part.value, Double::sum);
        }
        out.replaceAll((perk, sum) -> Math.min(sum, caps.applyAsDouble(perk)));
        return out;
    }
}
```

`src/fotfskills/perk/Chance.java`:

```java
package fotfskills.perk;

import java.util.function.DoubleSupplier;

/** Dice helpers with an injectable random source (tests pass fixed sequences). */
public final class Chance {
    private Chance() {
    }

    /** Each of amount points is saved with the given chance; returns the points that still apply. */
    public static int reduce(int amount, double chance, DoubleSupplier rnd) {
        return amount - successes(amount, chance, rnd);
    }

    public static int successes(int count, double chance, DoubleSupplier rnd) {
        if (chance <= 0) {
            return 0;
        }
        int hits = 0;
        for (int i = 0; i < count; i++) {
            if (rnd.getAsDouble() < chance) {
                hits++;
            }
        }
        return hits;
    }
}
```

`src/fotfskills/perk/Refund.java`:

```java
package fotfskills.perk;

import java.util.HashSet;
import java.util.List;

/** Ingredient refunds only for real recipes: at least two different items (no compress/decompress loops). */
public final class Refund {
    private Refund() {
    }

    public static boolean eligible(List<String> ingredientIds) {
        return new HashSet<>(ingredientIds).size() >= 2;
    }
}
```

`src/fotfskills/perk/Perks.java`:

```java
package fotfskills.perk;

import java.util.Map;
import java.util.concurrent.ThreadLocalRandom;
import net.minecraft.world.entity.player.Player;

/**
 * Perk ids, their caps, and every player's totals. Server totals come from PerkReward; the client reads the
 * copy PerkSync sends (only break speed needs it). tools/skills/perks.json may only use ids listed here.
 */
public final class Perks {
    public static final Map<String, Double> CAPS = Map.ofEntries(
            Map.entry("ore_drops", 0.95), Map.entry("ore_triple", 0.95), Map.entry("log_drops", 0.95),
            Map.entry("crop_drops", 0.95), Map.entry("harvest_double", 0.95), Map.entry("wild_drops", 0.95),
            Map.entry("bounty_triple", 0.95), Map.entry("seed_back", 0.95),
            Map.entry("pickaxe_durability", 0.95), Map.entry("armour_durability", 0.95),
            Map.entry("craft_save", 0.95), Map.entry("craft_free", 0.95), Map.entry("craft_arrows", 0.95),
            Map.entry("extra_serving", 0.95), Map.entry("double_catch", 0.95), Map.entry("animal_drops", 0.95),
            Map.entry("ammo_save", 0.95), Map.entry("treat_saver", 0.95), Map.entry("free_spell", 0.95),
            Map.entry("mining_speed", 2.0), Map.entry("deepslate_speed", 2.0), Map.entry("chop_speed", 2.0),
            Map.entry("draw_speed", 1.0), Map.entry("crit_damage", 2.0), Map.entry("projectile_damage", 2.0),
            Map.entry("executioner", 2.0), Map.entry("well_fed", 2.0), Map.entry("deep_delver", 2.0),
            Map.entry("fire_ward", 0.9), Map.entry("blast_ward", 0.9), Map.entry("fall_reduction", 0.9),
            Map.entry("bite_speed", 0.8), Map.entry("rain_bite_speed", 0.8), Map.entry("fall_immunity", 64.0));

    public static final PerkTotals TOTALS = new PerkTotals(perk -> CAPS.getOrDefault(perk, 0.0));

    private Perks() {
    }

    public static double get(Player player, String perk) {
        if (player.m_9236_().f_46443_) {
            return Math.min(ClientPerks.get(perk), CAPS.getOrDefault(perk, 0.0));
        }
        return TOTALS.total(player.m_20148_(), perk);
    }

    public static boolean roll(Player player, String perk) {
        double chance = get(player, perk);
        return chance > 0 && ThreadLocalRandom.current().nextDouble() < chance;
    }

    public static double random() {
        return ThreadLocalRandom.current().nextDouble();
    }
}
```

`src/fotfskills/perk/PerkReward.java`:

```java
package fotfskills.perk;

import net.minecraft.resources.ResourceLocation;
import net.puffish.skillsmod.api.SkillsAPI;
import net.puffish.skillsmod.api.reward.Reward;
import net.puffish.skillsmod.api.reward.RewardDisposeContext;
import net.puffish.skillsmod.api.reward.RewardUpdateContext;
import net.puffish.skillsmod.api.util.Problem;
import net.puffish.skillsmod.api.util.Result;

/** fotfskills:perk reward: {"perk": "ore_drops", "value": 0.03}. Each unlocked rank adds its value. */
public final class PerkReward implements Reward {
    private final String perk;
    private final double value;

    private PerkReward(String perk, double value) {
        this.perk = perk;
        this.value = value;
    }

    public static void register() {
        SkillsAPI.registerReward(new ResourceLocation("fotfskills", "perk"), context -> context.getData()
                .andThen(data -> data.getAsObject())
                .andThen(object -> object.getString("perk").andThen(perk -> object.getDouble("value")
                        .andThen(value -> Perks.CAPS.containsKey(perk)
                                ? Result.<PerkReward, Problem>success(new PerkReward(perk, value))
                                : Result.<PerkReward, Problem>failure(Problem.message("Unknown fotfskills perk: " + perk))))));
    }

    @Override
    public void update(RewardUpdateContext context) {
        Perks.TOTALS.put(context.getPlayer().m_20148_(), this, perk, value * context.getCount());
        PerkSync.markDirty(context.getPlayer());
    }

    @Override
    public void dispose(RewardDisposeContext context) {
        Perks.TOTALS.removeSource(this);
        context.getServer().m_6846_().m_11314_().forEach(PerkSync::markDirty);
    }
}
```

`src/fotfskills/perk/ClientPerks.java` (plain map, no client imports, safe on the server):

```java
package fotfskills.perk;

import java.util.HashMap;
import java.util.Map;

/** The local player's perk totals as last sent by the server (PerkSync). */
public final class ClientPerks {
    private static volatile Map<String, Double> totals = Map.of();

    private ClientPerks() {
    }

    static double get(String perk) {
        return totals.getOrDefault(perk, 0.0);
    }

    static void set(Map<String, Double> values) {
        totals = new HashMap<>(values);
    }
}
```

`src/fotfskills/perk/PerkSync.java`:

```java
package fotfskills.perk;

import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.network.NetworkDirection;
import net.minecraftforge.network.NetworkRegistry;
import net.minecraftforge.network.PacketDistributor;
import net.minecraftforge.network.simple.SimpleChannel;

/** Sends a player's perk totals to their client after changes (batched once per server tick). */
public final class PerkSync {
    private static final SimpleChannel CHANNEL = NetworkRegistry.newSimpleChannel(
            new ResourceLocation("fotfskills", "perks"), () -> "1", "1"::equals, "1"::equals);
    private static final Set<ServerPlayer> DIRTY = new HashSet<>();

    public record Totals(Map<String, Double> values) {
        static void encode(Totals msg, FriendlyByteBuf buf) {
            buf.m_130130_(msg.values.size());
            msg.values.forEach((perk, value) -> {
                buf.m_130070_(perk);
                buf.writeDouble(value);
            });
        }

        static Totals decode(FriendlyByteBuf buf) {
            int n = buf.m_130242_();
            Map<String, Double> values = new HashMap<>();
            for (int i = 0; i < n; i++) {
                values.put(buf.m_130277_(), buf.readDouble());
            }
            return new Totals(values);
        }
    }

    private PerkSync() {
    }

    public static void register() {
        CHANNEL.messageBuilder(Totals.class, 0, NetworkDirection.PLAY_TO_CLIENT)
                .encoder(Totals::encode).decoder(Totals::decode)
                .consumerMainThread((msg, context) -> {
                    ClientPerks.set(msg.values());
                    context.get().setPacketHandled(true);
                })
                .add();
    }

    public static synchronized void markDirty(ServerPlayer player) {
        DIRTY.add(player);
    }

    @SubscribeEvent
    public void onServerTick(TickEvent.ServerTickEvent event) {
        if (event.phase != TickEvent.Phase.END) {
            return;
        }
        Set<ServerPlayer> send;
        synchronized (PerkSync.class) {
            if (DIRTY.isEmpty()) {
                return;
            }
            send = new HashSet<>(DIRTY);
            DIRTY.clear();
        }
        for (ServerPlayer player : send) {
            if (!player.m_213877_()) {
                CHANNEL.send(PacketDistributor.PLAYER.with(() -> player), new Totals(Perks.TOTALS.snapshot(player.m_20148_())));
            }
        }
    }

    @SubscribeEvent
    public void onLogout(PlayerEvent.PlayerLoggedOutEvent event) {
        UUID id = event.getEntity().m_20148_();
        Perks.TOTALS.removePlayer(id);
        synchronized (PerkSync.class) {
            DIRTY.removeIf(p -> p.m_20148_().equals(id));
        }
    }
}
```

SRG names (check each with `javap`; fix in place if javac disagrees):

| SRG name | Method |
|---|---|
| m_6846_ | MinecraftServer.getPlayerList |
| m_11314_ | PlayerList.getPlayers |
| m_213877_ | Entity.isRemoved |

In `FotfSkills` constructor, add after `XpSources.register();`:

```java
        PerkReward.register();
        PerkSync.register();
        MinecraftForge.EVENT_BUS.register(new PerkSync());
```

(with imports `fotfskills.perk.PerkReward`, `fotfskills.perk.PerkSync`).

- [ ] **Step 4: Run test and build**

Run: `bash extras/fotfskills/test.sh`
Expected: `MoveBankTest ok` and `PerkLogicTest ok`.

Run: `bash extras/fotfskills/build.sh`
Expected: `Built fotfskills-1.0.0.jar`.

- [ ] **Step 5: Commit**

```bash
git add extras/fotfskills
git commit -m "Skills 2b: perk reward type, capped per-player totals, client sync"
```

---

### Task 2: Placed blocks and the break XP source

**Files:**
- Create: `extras/fotfskills/src/fotfskills/world/PlacedBlocks.java`, `extras/fotfskills/src/fotfskills/xp/BreakRules.java`, `extras/fotfskills/src/fotfskills/xp/BreakSource.java`, `extras/fotfskills/src/fotfskills/perk/BlockFacts.java`
- Create: `extras/fotfskills/test/fotfskills/xp/BreakRulesTest.java`
- Modify: `extras/fotfskills/src/fotfskills/xp/XpSources.java` (register `fotfskills:break`)
- Modify: `tools/skills/xp.json` (mining, forage, farm use `fotfskills:break`), `tools/skills/test_make_skill_trees.py`

**Interfaces:**
- Consumes: `AmountSource` registration pattern (2a).
- Produces:
  - `PlacedBlocks.of(ServerLevel)`, with `.mark(BlockPos)` and `.remove(BlockPos) -> boolean` (true if it was player-placed) and the static `tracked(BlockFacts)`.
  - `BreakRules.parse(com.google.gson.JsonObject)` and `.experience(BreakRules.Facts) -> int`.
  - `BlockFacts implements BreakRules.Facts` (wraps a BlockState: `hasTag`, `id`, `matureCrop`).
  - `BreakSource(BreakRules rules)`.

- [ ] **Step 1: Write the failing tests**

`extras/fotfskills/test/fotfskills/xp/BreakRulesTest.java`:

```java
package fotfskills.xp;

import com.google.gson.JsonParser;
import java.util.Set;

/** First matching rule wins; tags start with '#'; mature_crop needs a fully grown crop. Run: sh test.sh */
public final class BreakRulesTest {
    record Facts(String id, Set<String> tags, boolean matureCrop) implements BreakRules.Facts {
        public boolean hasTag(String tag) { return tags.contains(tag); }
    }

    public static void main(String[] args) {
        BreakRules rules = BreakRules.parse(JsonParser.parseString("""
            {"rules": [
              {"block": "#forge:ores/diamond", "experience": 20},
              {"block": "#forge:ores", "experience": 6},
              {"block": "minecraft:stone", "experience": 1},
              {"mature_crop": true, "experience": 3}
            ]}""").getAsJsonObject());
        check(rules.experience(new Facts("minecraft:diamond_ore", Set.of("forge:ores", "forge:ores/diamond"), false)) == 20, "diamond first");
        check(rules.experience(new Facts("minecraft:iron_ore", Set.of("forge:ores"), false)) == 6, "plain ore");
        check(rules.experience(new Facts("minecraft:stone", Set.of(), false)) == 1, "block id");
        check(rules.experience(new Facts("minecraft:wheat", Set.of("minecraft:crops"), true)) == 3, "grown crop");
        check(rules.experience(new Facts("minecraft:wheat", Set.of("minecraft:crops"), false)) == 0, "unripe crop");
        check(rules.experience(new Facts("minecraft:dirt", Set.of(), false)) == 0, "no rule");
        System.out.println("BreakRulesTest ok");
    }

    private static void check(boolean ok, String what) {
        if (!ok) { System.out.println("FAIL: " + what); System.exit(1); }
    }
}
```

Append to `tools/skills/test_make_skill_trees.py`:

```python
def test_gathering_xp_uses_the_placed_block_aware_source():
    for tree_id in ('mining', 'forage', 'farm'):
        types = [s['type'] for s in g.build_category(tree(tree_id), TIERS, xp=XP)['experience.json']['sources']]
        assert 'fotfskills:break' in types, tree_id
        assert not {'puffish_skills:mine_block', 'puffish_skills:break_block'} & set(types), tree_id
    farm = g.build_category(tree('farm'), TIERS, xp=XP)['experience.json']['sources']
    rules = next(s for s in farm if s['type'] == 'fotfskills:break')['data']['rules']
    assert rules == [{'mature_crop': True, 'experience': 3}]
```

- [ ] **Step 2: Run to verify they fail**

Run: `bash extras/fotfskills/test.sh` and `python -m pytest -q -p no:cacheprovider tools/skills`
Expected: the Java test fails on `cannot find symbol: class BreakRules`. The pytest test fails on `'fotfskills:break' in types`.

- [ ] **Step 3: Implement**

`src/fotfskills/xp/BreakRules.java`:

```java
package fotfskills.xp;

import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import java.util.ArrayList;
import java.util.List;

/** Ordered XP rules for broken blocks: {"rules": [{"block": "#tag" | "ns:id", "mature_crop": bool, "experience": n}]}. */
public final class BreakRules {
    public interface Facts {
        String id();

        boolean hasTag(String tag);

        boolean matureCrop();
    }

    private record Rule(String block, boolean matureCrop, int experience) {
        boolean matches(Facts facts) {
            if (matureCrop && !facts.matureCrop()) {
                return false;
            }
            if (block == null) {
                return true;
            }
            return block.startsWith("#") ? facts.hasTag(block.substring(1)) : block.equals(facts.id());
        }
    }

    private final List<Rule> rules;

    private BreakRules(List<Rule> rules) {
        this.rules = rules;
    }

    public static BreakRules parse(JsonObject data) {
        List<Rule> rules = new ArrayList<>();
        for (JsonElement element : data.getAsJsonArray("rules")) {
            JsonObject rule = element.getAsJsonObject();
            rules.add(new Rule(rule.has("block") ? rule.get("block").getAsString() : null,
                    rule.has("mature_crop") && rule.get("mature_crop").getAsBoolean(),
                    rule.get("experience").getAsInt()));
        }
        return new BreakRules(rules);
    }

    public int experience(Facts facts) {
        for (Rule rule : rules) {
            if (rule.matches(facts)) {
                return rule.experience;
            }
        }
        return 0;
    }
}
```

`src/fotfskills/xp/BreakSource.java`:

```java
package fotfskills.xp;

import net.puffish.skillsmod.api.experience.source.ExperienceSource;
import net.puffish.skillsmod.api.experience.source.ExperienceSourceDisposeContext;

/** fotfskills:break: XP for naturally generated blocks (BlockPerks skips player-placed ones). */
public record BreakSource(BreakRules rules) implements ExperienceSource {
    @Override
    public void dispose(ExperienceSourceDisposeContext context) {
    }
}
```

In `XpSources.register()` add:

```java
        SkillsAPI.registerExperienceSource(new ResourceLocation("fotfskills", "break"), context -> context.getData()
                .andThen(data -> {
                    try {
                        return Result.<BreakSource, Problem>success(new BreakSource(BreakRules.parse(data.getJson().getAsJsonObject())));
                    } catch (RuntimeException e) {
                        return Result.<BreakSource, Problem>failure(Problem.message("fotfskills:break rules: " + e.getMessage()));
                    }
                }));
```

`src/fotfskills/perk/BlockFacts.java`:

```java
package fotfskills.perk;

import fotfskills.xp.BreakRules;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.tags.TagKey;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.CropBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.IntegerProperty;
import net.minecraft.world.level.block.state.properties.Property;
import net.minecraftforge.registries.ForgeRegistries;

/** What the break rules and block perks need to know about a block state. */
public record BlockFacts(BlockState state) implements BreakRules.Facts {
    private static final Map<String, TagKey<Block>> TAGS = new ConcurrentHashMap<>();

    @Override
    public String id() {
        ResourceLocation key = ForgeRegistries.BLOCKS.getKey(state.m_60734_());
        return key == null ? "" : key.toString();
    }

    @Override
    public boolean hasTag(String tag) {
        return state.m_204336_(TAGS.computeIfAbsent(tag, t -> TagKey.m_203882_(ForgeRegistries.Keys.BLOCKS, new ResourceLocation(t))));
    }

    /** Fully grown: CropBlock.isMaxAge, or an "age" property at its maximum for other blocks in #minecraft:crops. */
    @Override
    public boolean matureCrop() {
        if (state.m_60734_() instanceof CropBlock crop) {
            return crop.m_52307_(state);
        }
        if (!hasTag("minecraft:crops")) {
            return false;
        }
        for (Property<?> property : state.m_61147_()) {
            if (property instanceof IntegerProperty age && age.m_61708_().equals("age")) {
                int max = age.m_6908_().stream().max(Integer::compare).orElse(0);
                return state.m_61143_(age) == max;
            }
        }
        return false;
    }
}
```

`src/fotfskills/world/PlacedBlocks.java`:

```java
package fotfskills.world;

import fotfskills.perk.BlockFacts;
import it.unimi.dsi.fastutil.longs.LongOpenHashSet;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.saveddata.SavedData;

/**
 * Positions of player-placed gathering blocks (ores, logs, stone, flowers, mushrooms) in one dimension, so
 * re-mining them gives no skill XP or extra drops. Saved as data/fotfskills_placed.dat in the dimension folder.
 */
public final class PlacedBlocks extends SavedData {
    private static final String NAME = "fotfskills_placed";
    private final LongOpenHashSet positions = new LongOpenHashSet();

    public static PlacedBlocks of(ServerLevel level) {
        return level.m_8895_().m_164861_(PlacedBlocks::load, PlacedBlocks::new, NAME);
    }

    public static boolean tracked(BlockFacts facts) {
        return facts.hasTag("forge:ores") || facts.hasTag("minecraft:logs")
                || facts.hasTag("minecraft:base_stone_overworld") || facts.hasTag("minecraft:base_stone_nether")
                || facts.hasTag("minecraft:flowers") || facts.id().endsWith("_mushroom");
    }

    private static PlacedBlocks load(CompoundTag tag) {
        PlacedBlocks data = new PlacedBlocks();
        for (long pos : tag.m_128467_("positions")) {
            data.positions.add(pos);
        }
        return data;
    }

    @Override
    public CompoundTag m_7176_(CompoundTag tag) {
        tag.m_128388_("positions", positions.toLongArray());
        return tag;
    }

    public void mark(BlockPos pos) {
        if (positions.add(pos.m_121878_())) {
            m_77762_();
        }
    }

    /** Forgets the position; true if it was player-placed. */
    public boolean remove(BlockPos pos) {
        boolean was = positions.remove(pos.m_121878_());
        if (was) {
            m_77762_();
        }
        return was;
    }
}
```

In `tools/skills/xp.json`, replace the `mining` and `forage` arrays and the farm `break_block` entry with:

```json
    "mining": [
      {"type": "fotfskills:break", "data": {"rules": [
        {"block": "#forge:ores/diamond", "experience": 20},
        {"block": "#forge:ores/emerald", "experience": 20},
        {"block": "#forge:ores", "experience": 6},
        {"block": "#minecraft:base_stone_overworld", "experience": 1},
        {"block": "#minecraft:base_stone_nether", "experience": 1}
      ]}}
    ],
    "forage": [
      {"type": "fotfskills:break", "data": {"rules": [
        {"block": "#minecraft:logs", "experience": 2},
        {"block": "#minecraft:flowers", "experience": 1},
        {"block": "minecraft:brown_mushroom", "experience": 1},
        {"block": "minecraft:red_mushroom", "experience": 1}
      ]}}
    ],
```

The farm entry `{"type": "fotfskills:break", "data": {"rules": [{"mature_crop": true, "experience": 3}]}}` stays first in `farm`, with the `increase_stat` bred source after it.

- [ ] **Step 4: Run tests**

Run: `bash extras/fotfskills/test.sh` and `python -m pytest -q -p no:cacheprovider tools/skills`
Expected: `BreakRulesTest ok` (plus the others) and pytest all passed (24).

The handler that marks/removes positions and pays the XP is in Task 3. Build only after Task 3.

- [ ] **Step 5: Commit**

```bash
python tools/skills/make_skill_trees.py
git add extras/fotfskills tools/skills config/puffish_skills
git commit -m "Skills 2b: placed-block tracking data and fotfskills:break XP source"
```

---

### Task 3: Perk hooks

**Files:**
- Create in `extras/fotfskills/src/fotfskills/perk/`: `BlockPerks.java`, `ItemPerks.java`, `CombatPerks.java`, `TamingPerks.java`, `IronsPerks.java`, `ArsPerks.java`
- Create in `extras/fotfskills/src/fotfskills/mixin/`: `ItemStackDurabilityMixin.java`, `FishingHookMixin.java`, `AbstractArrowAccessor.java`
- Modify: `mixin/ItemStackCraftedMixin.java` (extra serving), `res/fotfskills.mixins.json`, `FotfSkills.java`

**Interfaces:**
- Consumes: `Perks.get/roll`, `Chance`, `Refund`, `PlacedBlocks`, `BlockFacts`, `BreakSource` (Tasks 1–2). Perk ids from `Perks.CAPS`.
- Produces: game behaviour only.

- [ ] **Step 1: Write the code**

`BlockPerks.java`, which handles break XP, placed blocks, extra drops, seed back and break speed:

```java
package fotfskills.perk;

import fotfskills.world.PlacedBlocks;
import fotfskills.xp.BreakSource;
import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.enchantment.EnchantmentHelper;
import net.minecraft.world.item.enchantment.Enchantments;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.event.level.BlockEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.puffish.skillsmod.api.SkillsAPI;

/** Gathering: break XP (natural blocks only), extra drops, seed back, and mining/chopping speed. */
public final class BlockPerks {
    @SubscribeEvent(priority = EventPriority.LOWEST)
    public void onPlace(BlockEvent.EntityPlaceEvent event) {
        if (!event.isCanceled() && event.getEntity() instanceof ServerPlayer && event.getLevel() instanceof ServerLevel level
                && PlacedBlocks.tracked(new BlockFacts(event.getPlacedBlock()))) {
            PlacedBlocks.of(level).mark(event.getPos());
        }
    }

    /** LOWEST and skip cancelled: a claim mod that stops the break also stops XP and extra drops. */
    @SubscribeEvent(priority = EventPriority.LOWEST)
    public void onBreak(BlockEvent.BreakEvent event) {
        if (event.isCanceled() || !(event.getPlayer() instanceof ServerPlayer player)
                || !(event.getLevel() instanceof ServerLevel level)) {
            return;
        }
        BlockPos pos = event.getPos();
        BlockState state = event.getState();
        boolean placed = PlacedBlocks.of(level).remove(pos);
        if (placed || player.m_7500_() || (state.m_60834_() && !player.m_36298_(state))) {
            return;
        }
        BlockFacts facts = new BlockFacts(state);
        SkillsAPI.updateExperienceSources(player, BreakSource.class, source -> source.rules().experience(facts));

        ItemStack tool = player.m_21205_();
        boolean silk = EnchantmentHelper.m_44843_(Enchantments.f_44985_, tool) > 0;
        boolean fortune = EnchantmentHelper.m_44843_(Enchantments.f_44987_, tool) > 0;
        int copies = 0;
        if (facts.hasTag("forge:ores")) {
            if (!silk && !fortune) {          // spec: never on top of Fortune; silk would duplicate the ore block
                copies += Perks.roll(player, "ore_drops") ? 1 : 0;
                copies += Perks.roll(player, "ore_triple") ? 2 : 0;
            }
        } else if (facts.hasTag("minecraft:logs")) {
            copies += Perks.roll(player, "log_drops") ? 1 : 0;
            copies += Perks.roll(player, "bounty_triple") ? 2 : 0;
        } else if (facts.matureCrop()) {
            copies += Perks.roll(player, "crop_drops") ? 1 : 0;
            copies += Perks.roll(player, "harvest_double") ? 1 : 0;
            if (Perks.roll(player, "seed_back")) {
                Block.m_49840_(level, pos, state.m_60734_().m_7397_(level, pos, state));
            }
        } else if (facts.hasTag("minecraft:flowers") || facts.id().endsWith("_mushroom")) {
            copies += Perks.roll(player, "wild_drops") ? 1 : 0;
            copies += facts.id().endsWith("_mushroom") && Perks.roll(player, "bounty_triple") ? 2 : 0;
        }
        if (copies > 0 && !silk) {
            List<ItemStack> drops = Block.m_49874_(state, level, pos, level.m_7702_(pos), player, tool);
            for (int i = 0; i < copies; i++) {
                for (ItemStack drop : drops) {
                    Block.m_49840_(level, pos, drop.m_41777_());
                }
            }
        }
    }

    /** Runs on both sides; the client reads synced totals (PerkSync) so the crack animation matches. */
    @SubscribeEvent
    public void onBreakSpeed(PlayerEvent.BreakSpeed event) {
        BlockFacts facts = new BlockFacts(event.getState());
        double bonus = 0;
        if (facts.hasTag("minecraft:logs")) {
            bonus += Perks.get(event.getEntity(), "chop_speed");
        } else if (facts.hasTag("minecraft:mineable/pickaxe")) {
            bonus += Perks.get(event.getEntity(), "mining_speed");
            if (facts.id().contains("deepslate")) {
                bonus += Perks.get(event.getEntity(), "deepslate_speed");
            }
        }
        if (bonus > 0) {
            event.setNewSpeed((float) (event.getNewSpeed() * (1 + bonus)));
        }
    }
}
```

`ItemPerks.java`, which handles crafting refunds, extra arrows and double catch:

```java
package fotfskills.perk;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ThreadLocalRandom;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.tags.TagKey;
import net.minecraft.world.Container;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.event.entity.player.ItemFishedEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.items.ItemHandlerHelper;
import net.minecraftforge.registries.ForgeRegistries;

/** Crafting refunds (Frugal, Endless Workshop), Fletcher's extra arrows, and Double Catch. */
public final class ItemPerks {
    private static final TagKey<Item> ARROWS = TagKey.m_203882_(ForgeRegistries.Keys.ITEMS, new ResourceLocation("minecraft", "arrows"));

    /** Fires before the grid is consumed, so the ingredients are still there to copy. */
    @SubscribeEvent
    public void onCraft(PlayerEvent.ItemCraftedEvent event) {
        if (!(event.getEntity() instanceof ServerPlayer player)) {
            return;
        }
        Container grid = event.getInventory();
        List<ItemStack> refundable = new ArrayList<>();
        List<String> ids = new ArrayList<>();
        for (int i = 0; i < grid.m_6643_(); i++) {
            ItemStack stack = grid.m_8020_(i);
            if (!stack.m_41619_()) {
                ResourceLocation key = ForgeRegistries.ITEMS.getKey(stack.m_41720_());
                ids.add(key == null ? "" : key.toString());
                if (!stack.m_41720_().m_41470_()) {      // no bucket/bottle remainder
                    ItemStack one = stack.m_41777_();
                    one.m_41764_(1);
                    refundable.add(one);
                }
            }
        }
        if (Refund.eligible(ids) && !refundable.isEmpty()) {
            if (Perks.roll(player, "craft_free")) {
                refundable.forEach(stack -> ItemHandlerHelper.giveItemToPlayer(player, stack));
            } else if (Perks.roll(player, "craft_save")) {
                ItemHandlerHelper.giveItemToPlayer(player, refundable.get(ThreadLocalRandom.current().nextInt(refundable.size())));
            }
        }
        ItemStack result = event.getCrafting();
        if (result.m_204117_(ARROWS) && Perks.roll(player, "craft_arrows")) {
            ItemHandlerHelper.giveItemToPlayer(player, result.m_41777_());
        }
    }

    @SubscribeEvent
    public void onFished(ItemFishedEvent event) {
        if (event.getEntity() instanceof ServerPlayer player && Perks.roll(player, "double_catch")) {
            event.getDrops().forEach(stack -> ItemHandlerHelper.giveItemToPlayer(player, stack.m_41777_()));
        }
    }
}
```

`CombatPerks.java` handles ammo, draw speed, falls, wards, damage bonuses, crits and animal drops:

```java
package fotfskills.perk;

import fotfskills.mixin.AbstractArrowAccessor;
import java.util.ArrayList;
import java.util.Set;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.tags.TagKey;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.animal.Animal;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.world.entity.projectile.Projectile;
import net.minecraft.world.item.BowItem;
import net.minecraft.world.item.CrossbowItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.event.entity.EntityJoinLevelEvent;
import net.minecraftforge.event.entity.living.LivingDropsEvent;
import net.minecraftforge.event.entity.living.LivingEntityUseItemEvent;
import net.minecraftforge.event.entity.living.LivingFallEvent;
import net.minecraftforge.event.entity.living.LivingHurtEvent;
import net.minecraftforge.event.entity.player.CriticalHitEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.items.ItemHandlerHelper;
import net.minecraftforge.registries.ForgeRegistries;

/** Ammo saving, draw speed, falls, fire/blast wards, simple damage bonuses, crit damage, and butchering. */
public final class CombatPerks {
    private static final TagKey<Item> ARROWS = TagKey.m_203882_(ForgeRegistries.Keys.ITEMS, new ResourceLocation("minecraft", "arrows"));
    private static final Set<String> FIRE = Set.of("inFire", "onFire", "lava", "hotFloor", "fireball", "unattributedFireball");
    private static final Set<String> HIDES = Set.of("minecraft:leather", "minecraft:rabbit_hide", "minecraft:feather");

    /** Quiver Care: refund the arrow and make the fired one un-pickable, so nothing is duplicated. */
    @SubscribeEvent
    public void onJoin(EntityJoinLevelEvent event) {
        if (event.loadedFromDisk() || event.getLevel().f_46443_ || !(event.getEntity() instanceof AbstractArrow arrow)
                || !(arrow.m_19749_() instanceof ServerPlayer player) || arrow.f_36705_ != AbstractArrow.Pickup.ALLOWED) {
            return;
        }
        ItemStack ammo = ((AbstractArrowAccessor) arrow).fotfskills$pickupItem();
        if (ammo.m_204117_(ARROWS) && Perks.roll(player, "ammo_save")) {
            arrow.f_36705_ = AbstractArrow.Pickup.CREATIVE_ONLY;
            ItemHandlerHelper.giveItemToPlayer(player, ammo.m_41777_());
        }
    }

    /** Steady Hands / Rapid Volley: an extra tick of draw with the perk's chance (server decides arrow power). */
    @SubscribeEvent
    public void onUseTick(LivingEntityUseItemEvent.Tick event) {
        if (event.getEntity() instanceof ServerPlayer player
                && (event.getItem().m_41720_() instanceof BowItem || event.getItem().m_41720_() instanceof CrossbowItem)
                && Perks.random() < Perks.get(player, "draw_speed") && event.getDuration() > 1) {
            event.setDuration(event.getDuration() - 1);
        }
    }

    @SubscribeEvent
    public void onFall(LivingFallEvent event) {
        if (!(event.getEntity() instanceof ServerPlayer player)) {
            return;
        }
        if (event.getDistance() < Perks.get(player, "fall_immunity")) {
            event.setCanceled(true);
            return;
        }
        event.setDamageMultiplier((float) (event.getDamageMultiplier() * (1 - Perks.get(player, "fall_reduction"))));
    }

    @SubscribeEvent
    public void onHurt(LivingHurtEvent event) {
        LivingEntity target = event.getEntity();
        float amount = event.getAmount();
        String type = event.getSource().m_19385_();
        if (target instanceof ServerPlayer player) {
            if (FIRE.contains(type)) {
                amount *= (float) (1 - Perks.get(player, "fire_ward"));
            } else if (type.startsWith("explosion")) {
                amount *= (float) (1 - Perks.get(player, "blast_ward"));
            }
        }
        Entity attacker = event.getSource().m_7639_();
        if (attacker instanceof ServerPlayer player && attacker != target) {
            Entity direct = event.getSource().m_7640_();
            double bonus = 0;
            if (direct instanceof Projectile) {
                bonus += Perks.get(player, "projectile_damage");
            }
            if (direct == player && target.m_21223_() < 0.3f * target.m_21233_()) {
                bonus += Perks.get(player, "executioner");
            }
            if (player.m_20186_() < 40) {
                bonus += Perks.get(player, "deep_delver");
            }
            if (player.m_36324_().m_38702_() >= 20) {
                bonus += Perks.get(player, "well_fed");
            }
            amount *= (float) (1 + bonus);
        }
        event.setAmount(amount);
    }

    @SubscribeEvent
    public void onCrit(CriticalHitEvent event) {
        if (event.getEntity() instanceof ServerPlayer player && (event.isVanillaCritical() || event.getDamageModifier() > 1)) {
            event.setDamageModifier((float) (event.getDamageModifier() + Perks.get(player, "crit_damage")));
        }
    }

    /** Butcher / Husbandry: animals you kill may drop an extra copy of each meat, leather or feather stack. */
    @SubscribeEvent
    public void onDrops(LivingDropsEvent event) {
        if (!(event.getEntity() instanceof Animal animal) || !(event.getSource().m_7639_() instanceof ServerPlayer player)) {
            return;
        }
        for (ItemEntity drop : new ArrayList<>(event.getDrops())) {
            ItemStack stack = drop.m_32055_();
            ResourceLocation key = ForgeRegistries.ITEMS.getKey(stack.m_41720_());
            boolean animalGood = stack.m_41614_() || (key != null && HIDES.contains(key.toString()));
            if (animalGood && Perks.roll(player, "animal_drops")) {
                event.getDrops().add(new ItemEntity(animal.m_9236_(), animal.m_20185_(), animal.m_20186_(), animal.m_20189_(), stack.m_41777_()));
            }
        }
    }
}
```

`TamingPerks.java`:

```java
package fotfskills.perk;

import java.util.ArrayList;
import java.util.List;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.animal.Animal;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.player.PlayerInteractEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.items.ItemHandlerHelper;

/** Treat Saver: after you feed or tame an animal, the food it ate may come back. */
public final class TamingPerks {
    private record Fed(ServerPlayer player, InteractionHand hand, Item item, int before) {
    }

    private final List<Fed> pending = new ArrayList<>();

    @SubscribeEvent
    public void onInteract(PlayerInteractEvent.EntityInteract event) {
        if (event.getEntity() instanceof ServerPlayer player && event.getTarget() instanceof Animal animal) {
            ItemStack held = player.m_21120_(event.getHand());
            if (!held.m_41619_() && animal.m_6898_(held) && Perks.get(player, "treat_saver") > 0) {
                pending.add(new Fed(player, event.getHand(), held.m_41720_(), held.m_41613_()));
            }
        }
    }

    /** Checked one tick later: only food that was really used up is refunded. */
    @SubscribeEvent
    public void onServerTick(TickEvent.ServerTickEvent event) {
        if (event.phase != TickEvent.Phase.END || pending.isEmpty()) {
            return;
        }
        for (Fed fed : pending) {
            ItemStack now = fed.player.m_21120_(fed.hand);
            int count = now.m_150930_(fed.item) ? now.m_41613_() : 0;
            if (count == fed.before - 1 && Perks.roll(fed.player, "treat_saver")) {
                if (count > 0) {
                    now.m_41769_(1);
                } else {
                    ItemHandlerHelper.giveItemToPlayer(fed.player, new ItemStack(fed.item));
                }
            }
        }
        pending.clear();
    }
}
```

`IronsPerks.java` and `ArsPerks.java` (registered only when that mod is loaded):

```java
package fotfskills.perk;

import io.redspace.ironsspellbooks.api.events.SpellOnCastEvent;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;

/** Mana Saver / Archmage for Iron's Spells: the cast costs no mana. LOWEST so Magic XP (normal priority) still counts the real cost. */
public final class IronsPerks {
    @SubscribeEvent(priority = EventPriority.LOWEST)
    public void onCast(SpellOnCastEvent event) {
        if (event.getEntity() instanceof ServerPlayer player && Perks.roll(player, "free_spell")) {
            event.setManaCost(0);
        }
    }
}
```

```java
package fotfskills.perk;

import com.hollingsworth.arsnouveau.api.event.SpellCostCalcEvent;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.eventbus.api.SubscribeEvent;

/** Mana Saver / Archmage for Ars Nouveau: the spell costs no mana. */
public final class ArsPerks {
    @SubscribeEvent
    public void onCost(SpellCostCalcEvent event) {
        if (event.context.getUnwrappedCaster() instanceof ServerPlayer player && Perks.roll(player, "free_spell")) {
            event.currentCost = 0;
        }
    }
}
```

`mixin/ItemStackDurabilityMixin.java`:

```java
package fotfskills.mixin;

import fotfskills.perk.Chance;
import fotfskills.perk.Perks;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.util.RandomSource;
import net.minecraft.world.item.ArmorItem;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.PickaxeItem;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.ModifyVariable;

/** Steady Pick / Armour Care / Unbreakable: each point of durability loss may be saved. ItemStack.hurt = m_220157_. */
@Mixin(value = ItemStack.class, remap = false)
public abstract class ItemStackDurabilityMixin {
    @ModifyVariable(method = "m_220157_", at = @At("HEAD"), ordinal = 0, argsOnly = true, remap = false)
    private int fotfskills$saveDurability(int amount, int ignored, RandomSource random, ServerPlayer player) {
        if (player == null || amount <= 0) {
            return amount;
        }
        Object item = ((ItemStack) (Object) this).m_41720_();
        String perk = item instanceof PickaxeItem ? "pickaxe_durability" : item instanceof ArmorItem ? "armour_durability" : null;
        return perk == null ? amount : Chance.reduce(amount, Perks.get(player, perk), Perks::random);
    }
}
```

`mixin/FishingHookMixin.java`:

```java
package fotfskills.mixin;

import fotfskills.perk.Perks;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.projectile.FishingHook;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.ModifyArg;

/**
 * Patient Angler / Storm Fisher: shorter wait for a bite. catchingFish (m_37145_) rolls the wait with
 * Mth.nextInt(random, 100, 600) (third nextInt call, ordinal 2); both bounds are scaled down.
 */
@Mixin(value = FishingHook.class, remap = false)
public abstract class FishingHookMixin {
    @ModifyArg(method = "m_37145_", remap = false, index = 1, at = @At(value = "INVOKE",
            target = "Lnet/minecraft/util/Mth;m_216271_(Lnet/minecraft/util/RandomSource;II)I", ordinal = 2, remap = false))
    private int fotfskills$minWait(int min) {
        return scaled(min);
    }

    @ModifyArg(method = "m_37145_", remap = false, index = 2, at = @At(value = "INVOKE",
            target = "Lnet/minecraft/util/Mth;m_216271_(Lnet/minecraft/util/RandomSource;II)I", ordinal = 2, remap = false))
    private int fotfskills$maxWait(int max) {
        return scaled(max);
    }

    private int scaled(int ticks) {
        FishingHook hook = (FishingHook) (Object) this;
        if (!(hook.m_37168_() instanceof ServerPlayer player)) {
            return ticks;
        }
        double faster = Perks.get(player, "bite_speed");
        BlockPos pos = hook.m_20183_();
        if (hook.m_9236_().m_46758_(pos.m_7494_())) {
            faster += Perks.get(player, "rain_bite_speed");
        }
        return Math.max(1, (int) Math.round(ticks * (1 - Math.min(faster, 0.8))));
    }
}
```

`BlockPos.m_7494_` is above(). Verify it with javap.

`mixin/AbstractArrowAccessor.java`:

```java
package fotfskills.mixin;

import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.world.item.ItemStack;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Invoker;

/** AbstractArrow.getPickupItem (m_7941_) is protected; Quiver Care needs the item to refund. */
@Mixin(value = AbstractArrow.class, remap = false)
public interface AbstractArrowAccessor {
    @Invoker(value = "m_7941_", remap = false)
    ItemStack fotfskills$pickupItem();
}
```

`ItemStackCraftedMixin.java` gets Extra Serving. In the edible branch, after the cook XP award:

```java
                int extra = Chance.successes(amount, Perks.get(server, "extra_serving"), Perks::random);
                if (extra > 0) {
                    ItemStack bonus = stack.m_41777_();
                    bonus.m_41764_(extra);
                    net.minecraftforge.items.ItemHandlerHelper.giveItemToPlayer(server, bonus);
                }
```

(with imports `fotfskills.perk.Chance` and `fotfskills.perk.Perks`).

In `res/fotfskills.mixins.json`:

```json
  "mixins": ["ItemStackCraftedMixin", "ItemStackDurabilityMixin", "FishingHookMixin", "AbstractArrowAccessor"],
```

In the `FotfSkills` constructor, after `MinecraftForge.EVENT_BUS.register(new PerkSync());`:

```java
        MinecraftForge.EVENT_BUS.register(new BlockPerks());
        MinecraftForge.EVENT_BUS.register(new ItemPerks());
        MinecraftForge.EVENT_BUS.register(new CombatPerks());
        MinecraftForge.EVENT_BUS.register(new TamingPerks());
```

Inside the existing `irons_spellbooks` / `ars_nouveau` checks, also register `new IronsPerks()` / `new ArsPerks()`.

- [ ] **Step 2: Build and run the tests**

Run: `bash extras/fotfskills/test.sh`
Expected: `MoveBankTest ok`, `PerkLogicTest ok`, `BreakRulesTest ok`.

Run: `bash extras/fotfskills/build.sh`
Expected: `Built fotfskills-1.0.0.jar`. Any SRG name javac rejects gets corrected after a `javap` check (Ruling only if behaviour changes).

- [ ] **Step 3: Commit**

```bash
git add extras/fotfskills
git commit -m "Skills 2b: perk hooks (drops, durability, refunds, ammo, draw, fishing, wards, damage, taming, mana)"
```

---

### Task 4: Wire the perks into the trees

**Files:**
- Modify: `tools/skills/perks.json`, `tools/skills/test_make_skill_trees.py`

**Interfaces:**
- Consumes: perk ids in `extras/fotfskills/src/fotfskills/perk/Perks.java` (`Map.entry("<id>", cap)`).
- Produces: rank definitions with `fotfskills:perk` rewards.

- [ ] **Step 1: Write the failing tests**

Replace `test_perks_only_name_real_nodes_and_valid_operations` with:

```python
PERK_IDS = set(re.findall(r'Map\.entry\("([a-z_]+)"',
                          (Path(__file__).parents[2] / 'extras/fotfskills/src/fotfskills/perk/Perks.java').read_text(encoding='utf-8')))


def test_perks_only_name_real_nodes_and_known_perks():
    assert 'ore_drops' in PERK_IDS
    for tree_id, nodes in PERKS.items():
        slugs = {g.slug(n['name']) for n in tree(tree_id)['nodes']}
        for node_slug, rewards in nodes.items():
            assert node_slug in slugs, (tree_id, node_slug)
            for r in rewards:
                if r['type'] == 'puffish_skills:attribute':
                    assert r['data']['operation'] in {'addition', 'multiply_base', 'multiply_total'}
                else:
                    assert r['type'] == 'fotfskills:perk' and r['data']['perk'] in PERK_IDS, r
                    assert r['data']['value'] > 0


def test_common_perk_nodes_are_wired():
    expect = {('mining', 'prospector_1'): ('ore_drops', 0.03), ('range', 'quiver_care_2'): ('ammo_save', 0.08),
              ('craft', 'endless_workshop_1'): ('craft_free', 0.1), ('fish', 'patient_angler_1'): ('bite_speed', 0.05),
              ('agility', 'featherfall_1'): ('fall_immunity', 15), ('defense', 'unbreakable_1'): ('armour_durability', 0.5)}
    for (tree_id, sid), (perk, value) in expect.items():
        defs = g.build_category(tree(tree_id), TIERS, XP, PERKS)['definitions.json']
        assert {'type': 'fotfskills:perk', 'data': {'perk': perk, 'value': value}} in defs[sid]['rewards'], sid
```

Add `import re` at the top of the test file.

- [ ] **Step 2: Run to verify it fails**

Run: `python -m pytest -q -p no:cacheprovider tools/skills`
Expected: `test_common_perk_nodes_are_wired` FAILS with KeyError 'rewards' on `prospector_1`.

- [ ] **Step 3: Add the perk nodes to `tools/skills/perks.json`**

Merge these entries into the existing file; keep the 2a attribute entries. Archmage also gets its attribute. `P(id, v)` is shorthand for `{"type": "fotfskills:perk", "data": {"perk": "<id>", "value": v}}`; write the full objects in the file.

| Tree | Node slug | Reward(s) |
|---|---|---|
| mining | stone_sense | P(mining_speed, 0.04) |
| mining | steady_pick | P(pickaxe_durability, 0.05) |
| mining | prospector, prospector_ii | P(ore_drops, 0.03) |
| mining | bedrock_grip | P(deepslate_speed, 0.06) |
| mining | deep_delver | P(deep_delver, 0.05) |
| mining | motherlode | P(ore_triple, 0.02) |
| forage | lumberjack | P(chop_speed, 0.04) |
| forage | timber, timber_ii | P(log_drops, 0.03) |
| forage | wildcrafter | P(wild_drops, 0.08) |
| forage | fletcher | P(craft_arrows, 0.1) |
| forage | natures_bounty | P(bounty_triple, 0.05) |
| farm | harvester, harvester_ii | P(crop_drops, 0.03) |
| farm | seed_saver | P(seed_back, 0.08) |
| farm | harvest_moon | P(harvest_double, 0.05) |
| fish | patient_angler, patient_angler_ii | P(bite_speed, 0.05) |
| fish | storm_fisher | P(rain_bite_speed, 0.1) |
| fish | double_catch | P(double_catch, 0.04) |
| cook | extra_serving | P(extra_serving, 0.05) |
| cook | well_fed | P(well_fed, 0.02) |
| craft | frugal, frugal_ii | P(craft_save, 0.03) |
| craft | endless_workshop | P(craft_free, 0.1) |
| attack | crit_training | P(crit_damage, 0.05) |
| attack | executioner | P(executioner, 0.15) |
| attack | butcher | P(animal_drops, 0.1) |
| range | steady_hands | P(draw_speed, 0.05) |
| range | rapid_volley | P(draw_speed, 0.15) |
| range | sharp_tips | P(projectile_damage, 0.04) |
| range | heavy_draw | P(projectile_damage, 0.12) |
| range | quiver_care, quiver_care_ii | P(ammo_save, 0.08) |
| range | fletchers_luck | P(ammo_save, 0.3) |
| defense | fire_ward | P(fire_ward, 0.15) |
| defense | blast_ward | P(blast_ward, 0.15) |
| defense | armour_care | P(armour_durability, 0.05) |
| defense | unbreakable | P(armour_durability, 0.5) |
| agility | soft_landing | P(fall_reduction, 0.06) |
| agility | featherfall | P(fall_immunity, 15) |
| magic | mana_saver | P(free_spell, 0.04) |
| magic | archmage | P(free_spell, 0.12) + attribute irons_spellbooks:cooldown_reduction 0.15 addition |
| taming | treat_saver | P(treat_saver, 0.1) |
| taming | husbandry | P(animal_drops, 0.04) |

- [ ] **Step 4: Run tests**

Run: `python -m pytest -q -p no:cacheprovider tools/skills`
Expected: all passed (26).

- [ ] **Step 5: Commit**

```bash
python tools/skills/make_skill_trees.py
git add tools/skills config/puffish_skills
git commit -m "Skills 2b: common perk nodes wired to fotfskills:perk rewards"
```

---

### Task 5: Pack, boot and in-game check

- [ ] **Step 1: Pack and push**

```bash
H=$(sha512sum extras/fotfskills/fotfskills-1.0.0.jar | cut -d' ' -f1)
sed -i "s/^hash = .*/hash = \"$H\"/" mods/fotfskills.pw.toml
packwiz refresh
git add mods/fotfskills.pw.toml index.toml pack.toml && git commit -m "Skills 2b: ship rebuilt add-on"
git push origin skills-preview
cd ../server-test && docker compose down && PACK_REF=$(git -C ../pack rev-parse HEAD) docker compose up -d
```

- [ ] **Step 2: Boot log**

Run: `docker logs fotf-test 2>&1 | grep -E "Done \(|\[puffish_skills|fotfskills|Mixin.*(rror|fail)|Unknown fotfskills perk"`
Expected: `Mod configuration loaded successfully!` and no fotfskills/mixin errors.

- [ ] **Step 3: In-game check with Dylan** (combined with the 2a XP table, which he deferred)

Grant points with `/puffish_skills points set @a <tree> 50` and take the nodes. Then:

| Do | Expect |
|---|---|
| Place an iron ore and mine it | No Mining XP, no extra drops |
| Mine natural ores with Prospector ×5 | Occasional extra raw iron, never with Fortune/Silk Touch |
| Stone Sense ×5 | Stone breaks visibly faster (client animation too) |
| Frugal + craft a pickaxe repeatedly | Sometimes an ingredient back; un-crafting an iron block never refunds |
| Quiver Care: shoot arrows | Sometimes the arrow returns to your inventory and the fired one can't be picked up |
| Patient Angler ×5 | Bites come noticeably sooner |
| Featherfall: jump off 10 blocks | No damage |
| Fire Ward ×2: stand in fire | Less damage |
| Treat Saver: breed cows repeatedly | Sometimes the wheat isn't used |
| Mana Saver: cast repeatedly | Some casts cost no mana |

A failing row is debugged (systematic-debugging) before the task completes, or moved to phase 3 as a Ruling.
