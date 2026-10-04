package fotfskills.perk;

/** Resetting a tree costs 1 XP level per 2 points spent in it, at least 5. */
public final class ResetCost {
    private ResetCost() {
    }

    public static int levels(int spentPoints) {
        return Math.max(5, (spentPoints + 1) / 2);
    }
}
