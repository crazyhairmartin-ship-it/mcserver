package fotfskills.perk;

/** Consecutive actions within a window of ticks, capped (Momentum stacks, Flurry's every-5th-hit count). */
public final class Streak {
    private final long window;
    private final int max;
    private long last = Long.MIN_VALUE / 2;
    private int count;

    public Streak(long window, int max) {
        this.window = window;
        this.max = max;
    }

    public int hit(long now) {
        count = now - last <= window ? Math.min(count + 1, max) : 1;
        last = now;
        return count;
    }

    public void reset() {
        count = 0;
    }
}
