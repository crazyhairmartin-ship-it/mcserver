package fotfskills.perk;

import java.util.Map;
import java.util.Random;

/** Pure rules behind the deferred nodes (phase 5) and the small fixes. Run: sh test.sh */
public final class DeferredNodesTest {
    public static void main(String[] args) {
        // Quick Hands / Smelter: fractional extra ticks add up
        StationBoost.Ticks ticks = new StationBoost.Ticks();
        int extra = 0;
        for (int i = 0; i < 8; i++) {
            extra += ticks.extra(0.25);
        }
        check(extra == 2, "25% faster = 2 extra ticks in 8");
        check(new StationBoost.Ticks().extra(0) == 0, "no perk, no extra ticks");
        check(new StationBoost.Ticks().extra(1.5) == 1 , "first tick of 150%: 1 extra (0.5 carried)");

        // Feast Maker: a serving was taken when servings drops by 1 or bites rises by 1
        check(ServingRule.taken("servings", 4, 3), "feast serving taken");
        check(ServingRule.taken("bites", 0, 1), "pie / cake slice taken");
        check(ServingRule.taken("cuts", 1, 2), "Let's Do pie / cake slice taken (cuts)");
        check(!ServingRule.taken("servings", 3, 3) && !ServingRule.taken("bites", 2, 1), "nothing taken");
        check(!ServingRule.taken("age", 1, 2), "other properties never count");

        // Irrigator: vanilla reach is 4 blocks, +1 per rank
        check(Irrigation.reach(0) == 4 && Irrigation.reach(3) == 7, "irrigation reach");

        // Tunnel Vision: Ultimine hunger scaled down, never below 10%
        check(Math.abs(Tunnel.scale(1.0f, 0.6) - 0.4f) < 1e-6, "4 ranks: 60% less hunger");
        check(Math.abs(Tunnel.scale(1.0f, 2.0) - 0.1f) < 1e-6, "capped at 90% off");

        // Brewer: effects a drink added or refreshed last longer
        check(DrinkRule.extended(0, 600, 0.2) == 720, "new effect from the drink: +20%");
        check(DrinkRule.extended(900, 600, 0.2) == -1, "effect you already had for longer: untouched");
        check(DrinkRule.extended(100, 600, 0) == -1, "no perk: untouched");

        // Bloodlines: rare looks for vanilla babies
        Random random = new Random(1);
        check(Bloodlines.rare("minecraft:axolotl", random).equals(Map.of("Variant", 4)), "blue axolotl");
        java.util.Set<Object> colours = new java.util.HashSet<>();
        for (int i = 0; i < 400; i++) {
            colours.add(Bloodlines.rare("minecraft:sheep", random).get("Color"));
        }
        check(colours.equals(java.util.Set.of((byte) 15, (byte) 7, (byte) 8, (byte) 12, (byte) 9, (byte) 3, (byte) 11,
                (byte) 4, (byte) 1, (byte) 14, (byte) 6)), "sheep: the 11 rare colours, nothing else: " + colours);
        check(Bloodlines.rare("minecraft:goat", random).equals(Map.of("IsScreamingGoat", true)), "screaming goat");
        check(Bloodlines.rare("minecraft:panda", random).equals(Map.of("MainGene", "brown", "HiddenGene", "brown")), "brown panda");
        int horse = (int) Bloodlines.rare("minecraft:horse", random).get("Variant");
        check((horse & 0xFF) <= 6 && (horse >> 8) >= 1 && (horse >> 8) <= 4, "horse with markings");
        check(Bloodlines.rare("alexsmobs:elephant", random).isEmpty(), "modded animals unchanged");

        // Prized Stock: parents can breed again sooner (vanilla cooldown 6000 ticks)
        check(Breeding.cooldown(6000, 0.5) == 3000, "half the breeding cooldown");
        check(Breeding.cooldown(6000, 0) == 6000 && Breeding.cooldown(6000, 2) == 600, "no perk unchanged; never under 30 s");

        // Steady Hands: deterministic extra draw ticks (client and server agree)
        int drawn = 0, drawTicks = 0;
        for (int elapsed = 0; drawn < 20; drawTicks++) {
            int e = DrawRule.extra(elapsed, 0.25);
            drawn += 1 + e;
            elapsed += 1 + e;
        }
        check(drawTicks >= 16 && drawTicks <= 17, "25% faster: a 20-tick draw takes 16-17 ticks (got " + drawTicks + ")");
        check(DrawRule.extra(5, 0) == 0, "no perk, no extra");

        // Seeker fix: Arcane Arrows only spends mana on a real full draw, not a crit Seeker added
        check(!RangePerks.arcaneShot(false, 1), "Seeker crit on a quick shot: no mana spent");
        check(RangePerks.arcaneShot(true, 1) && !RangePerks.arcaneShot(true, 0), "full draw with the perk only");
        System.out.println("DeferredNodesTest ok");
    }

    private static void check(boolean ok, String what) {
        if (!ok) { System.out.println("FAIL: " + what); System.exit(1); }
    }
}
