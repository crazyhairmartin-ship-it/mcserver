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
