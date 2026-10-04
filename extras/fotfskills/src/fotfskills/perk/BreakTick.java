package fotfskills.perk;

/**
 * Ultimine compensation: FTB Ultimine (and Sweeping Harvest) break a whole vein in one tick. The first block a player
 * breaks in a tick gives full gathering XP; the others give a share, rounded by chance so small amounts still count.
 * Logs get a gentler share than ore and stone, since a tree is a handful of logs and a vein or tunnel is many blocks.
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

    /** The share for this block: full for the first block of the tick, LOG_SHARE for later logs, factor otherwise. */
    public static double share(double factor, boolean log) {
        return factor < 1 && log ? LOG_SHARE : factor;
    }

    /** xp x factor: the whole part, plus one more with the leftover fraction as the chance. */
    public static int scale(int xp, double factor, double roll) {
        double value = xp * factor;
        int whole = (int) Math.floor(value);
        return whole + (roll < value - whole ? 1 : 0);
    }
}
