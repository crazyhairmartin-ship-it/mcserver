package fotfskills.perk;

/**
 * Ultimine compensation: FTB Ultimine (and Sweeping Harvest) break a whole vein in one tick. The first block a player
 * breaks in a tick gives full gathering XP; the others give a share, rounded by chance so small amounts still count.
 */
public final class BreakTick {
    private final double later;
    private long tick = Long.MIN_VALUE;

    public BreakTick(double later) {
        this.later = later;
    }

    public double factor(long now) {
        if (now != tick) {
            tick = now;
            return 1.0;
        }
        return later;
    }

    /** xp x factor: the whole part, plus one more with the leftover fraction as the chance. */
    public static int scale(int xp, double factor, double roll) {
        double value = xp * factor;
        int whole = (int) Math.floor(value);
        return whole + (roll < value - whole ? 1 : 0);
    }
}
