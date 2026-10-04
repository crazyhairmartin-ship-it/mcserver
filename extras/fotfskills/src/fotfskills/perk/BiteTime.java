package fotfskills.perk;

/**
 * Patient Angler / Storm Fisher scale the bite wait AFTER vanilla subtracts Lure. A wait Lure already brought to 0 or
 * below is left alone (vanilla re-rolls it), so the perk can never make fish stop biting.
 */
public final class BiteTime {
    private BiteTime() {
    }

    public static int scale(int ticks, double faster) {
        if (ticks <= 0) {
            return ticks;
        }
        return Math.max(1, (int) Math.round(ticks * (1 - Math.min(faster, 0.8))));
    }
}
