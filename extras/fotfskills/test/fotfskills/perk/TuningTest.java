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
        check(Tuning.enchantLevel(3, 2, 4, 0.99) == 3, "Enchanted Crafts II adds levels, never above III (low-level enchantments, spec)");
        check(Tuning.enchantLevel(1, 1, 5, 0.0) == 2, "bonus raises a level-I roll to II");
        check(Tuning.enchantLevel(3, 1, 1, 0.5) == 1, "single-level enchantments stay at I");
        System.out.println("TuningTest ok");
    }

    private static void check(boolean ok, String what) {
        if (!ok) { System.out.println("FAIL: " + what); System.exit(1); }
    }
}
