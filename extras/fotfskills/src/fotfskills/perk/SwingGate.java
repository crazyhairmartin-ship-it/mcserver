package fotfskills.perk;

/**
 * True for the first melee hit a player lands in a game tick: the swing's main target. A sweep hits the other targets
 * in the same tick, and those must not build streaks or spend once-per-swing bonuses (Counter, Spellbound Steel).
 */
public final class SwingGate {
    private long lastTick = Long.MIN_VALUE;

    public boolean first(long now) {
        if (now == lastTick) {
            return false;
        }
        lastTick = now;
        return true;
    }
}
