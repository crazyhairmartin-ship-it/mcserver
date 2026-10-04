package fotfskills.perk;

/**
 * Ultimine compensation: FTB Ultimine (and Sweeping Harvest) break a whole vein in one tick. The first block a player
 * breaks in a tick gives full gathering XP; the others give a share, rounded by chance so small amounts still count.
 * Ores always give full XP; logs get a gentler share than stone, since a tree is a handful of logs and a tunnel is many.
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

    public static final double LOG_SHARE = 0.6;

    /** What kind of block it is, for the Ultimine share. */
    public enum Kind { ORE, LOG, OTHER }

    /**
     * The share for this block: ores always give full XP; after the first block of the tick, logs give LOG_SHARE and
     * everything else (stone) gives factor.
     */
    public static double share(double factor, Kind kind) {
        if (kind == Kind.ORE || factor >= 1) {
            return 1.0;
        }
        return kind == Kind.LOG ? LOG_SHARE : factor;
    }

    /** xp x factor: the whole part, plus one more with the leftover fraction as the chance. */
    public static int scale(int xp, double factor, double roll) {
        double value = xp * factor;
        int whole = (int) Math.floor(value);
        return whole + (roll < value - whole ? 1 : 0);
    }
}
