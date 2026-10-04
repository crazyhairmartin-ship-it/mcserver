package fotfskills.perk;

/** Total-level hearts and tree reset cost. Run: sh test.sh */
public final class Phase4LogicTest {
    public static void main(String[] args) {
        check(HeartCurve.steps(0) == 0 && HeartCurve.steps(7) == 0, "no hearts before total level 8");
        check(HeartCurve.steps(8) == 1 && HeartCurve.steps(18) == 1 && HeartCurve.steps(19) == 2, "spec thresholds");
        check(HeartCurve.steps(255) == 14 && HeartCurve.steps(256) == 15 && HeartCurve.steps(600) == 15, "15 hearts by 256");
        check(ResetCost.levels(0) == 5 && ResetCost.levels(9) == 5 && ResetCost.levels(11) == 6, "1 per 2 points, minimum 5");
        check(ResetCost.levels(50) == 25, "a full tree costs 25 levels");
        System.out.println("Phase4LogicTest ok");
    }

    private static void check(boolean ok, String what) {
        if (!ok) { System.out.println("FAIL: " + what); System.exit(1); }
    }
}
