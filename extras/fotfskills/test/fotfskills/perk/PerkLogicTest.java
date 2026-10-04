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
