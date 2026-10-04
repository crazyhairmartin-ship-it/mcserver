package fotfskills.perk;

/** A per-player cooldown in ticks (Second Wind). */
public final class Cooldown {
    private final long ticks;
    private long readyAt;

    public Cooldown(long ticks) {
        this.ticks = ticks;
    }

    public boolean ready(long now) {
        return now >= readyAt;
    }

    public void trigger(long now) {
        readyAt = now + ticks;
    }
}
