package fotfskills.xp;

/** Plain-java test (no JUnit in the build container): exits non-zero on failure. Run: sh test.sh */
public final class MoveBankTest {
    public static void main(String[] args) {
        MoveBank bank = new MoveBank();
        check(bank.add(0.28, 20) == 0, "a sprint tick is not a whole XP");
        for (int i = 0; i < 70; i++) bank.add(0.28, 20);       // 71 ticks x 0.28 m = 19.88 m
        check(bank.add(0.28, 20) == 1, "the 72nd tick crosses 20 m");
        check(bank.add(45, 20) == 2, "45 m more gives 2 and keeps 5.16 m");
        check(Math.abs(bank.remainder() - 5.16) < 1e-6, "remainder kept");
        check(AmountSource.scaled(0.3, 1.0) == 1, "a positive amount gives at least 1 XP");
        check(AmountSource.scaled(0, 1.0) == 0, "zero gives none");
        check(AmountSource.scaled(7, 1.5) == 11, "7 x 1.5 = 10.5 rounds to 11");
        System.out.println("MoveBankTest ok");
    }

    private static void check(boolean ok, String what) {
        if (!ok) { System.out.println("FAIL: " + what); System.exit(1); }
    }
}
