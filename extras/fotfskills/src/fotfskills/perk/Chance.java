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
