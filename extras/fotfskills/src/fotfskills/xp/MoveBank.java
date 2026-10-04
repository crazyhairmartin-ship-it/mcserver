package fotfskills.xp;

/** Banks distance between ticks: Pufferfish rounds each XP event, so tiny per-tick amounts must be pooled. */
public final class MoveBank {
    private double meters;

    /** Adds distance; returns whole XP earned (one per metersPerXp) and keeps the remainder. */
    public int add(double moved, double metersPerXp) {
        meters += moved;
        int xp = (int) Math.floor(meters / metersPerXp);
        meters -= xp * metersPerXp;
        return xp;
    }

    public double remainder() {
        return meters;
    }
}
