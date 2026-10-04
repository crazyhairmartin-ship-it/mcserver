package fotfskills.perk;

/** Spec rev 5: heart step k of 15 needs 256 x (k/15)^1.3 total skill levels. */
public final class HeartCurve {
    public static final int[] THRESHOLDS = {8, 19, 32, 46, 61, 78, 95, 113, 132, 151, 171, 192, 213, 234, 256};

    private HeartCurve() {
    }

    public static int steps(int totalLevel) {
        int steps = 0;
        for (int threshold : THRESHOLDS) {
            if (totalLevel >= threshold) {
                steps++;
            }
        }
        return steps;
    }
}
