package fotfskills.mana;

/** Shared mana conversions. Run: sh test.sh */
public final class ManaMathTest {
    public static void main(String[] args) {
        check(ManaMath.maxBonus(100, 100) == 0, "Ars at its base adds nothing");
        check(ManaMath.maxBonus(265, 100) == 165, "glyphs, book tier and gear above Ars's base add to the pool");
        check(ManaMath.maxBonus(80, 100) == 0, "never negative (reserved mana)");
        // Ars adds its per-second regen on both tick phases, so 2 nominal extra = 4 mana/s really; Iron's gives
        // max x 0.02 x regen x multiplier per second -> 4 / (200 x 0.02) = +1.0 regen
        check(Math.abs(ManaMath.regenBonus(7, 5, 200, 1.0) - 1.0) < 1e-9, "Ars regen above its base becomes the same real mana/s on Iron's");
        check(ManaMath.regenBonus(5, 5, 200, 1.0) == 0, "Ars base regen adds nothing (Iron's own regen is the base)");
        check(ManaMath.regenBonus(9, 5, 0, 1.0) == 0, "no pool, no division by zero");
        System.out.println("ManaMathTest ok");
    }

    private static void check(boolean ok, String what) {
        if (!ok) { System.out.println("FAIL: " + what); System.exit(1); }
    }
}
