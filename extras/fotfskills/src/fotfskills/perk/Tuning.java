package fotfskills.perk;

/** Small formulas for Sea Legs and Enchanted Crafts. */
public final class Tuning {
    private Tuning() {
    }

    /** Per-tick horizontal velocity factor that makes a boat's top speed on water (friction 0.9) 1 + faster times higher. */
    public static double boatFactor(double faster) {
        return (1 - 0.1 / (1 + faster)) / 0.9;
    }

    /** A level uniform in 1..cap, plus bonus, within 1..maxLevel and never above III (low-level enchantments, spec). */
    public static int enchantLevel(int cap, int bonus, int maxLevel, double roll) {
        int level = 1 + (int) Math.floor(roll * Math.max(cap, 1)) + bonus;
        return Math.max(1, Math.min(level, Math.min(maxLevel, 3)));
    }
}
