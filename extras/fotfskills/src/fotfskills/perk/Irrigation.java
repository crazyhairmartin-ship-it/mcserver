package fotfskills.perk;

/** Irrigator: vanilla farmland finds water up to 4 blocks away; each rank adds one block. */
public final class Irrigation {
    public static final int VANILLA = 4;

    private Irrigation() {
    }

    public static int reach(int rank) {
        return VANILLA + rank;
    }
}
