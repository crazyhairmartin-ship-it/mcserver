package fotfskills.perk;

/** Ultimine compensation: blocks broken in the same tick after the first give a quarter of the XP. Run: sh test.sh */
public final class BreakTickTest {
    public static void main(String[] args) {
        BreakTick breaks = new BreakTick(0.25);
        check(breaks.factor(100) == 1.0, "the block you mined gives full XP");
        check(breaks.factor(100) == 0.25, "the rest of the vein in that tick gives a quarter");
        check(breaks.factor(100) == 0.25, "still a quarter");
        check(breaks.factor(101) == 1.0, "the next tick starts over");

        check(BreakTick.scale(6, 1.0, 0.99) == 6, "full XP unchanged");
        check(BreakTick.scale(6, 0.25, 0.99) == 1, "6 x 0.25 = 1.5: 1 plus a 50% chance of 1 more (roll missed)");
        check(BreakTick.scale(6, 0.25, 0.1) == 2, "roll hit");
        check(BreakTick.scale(1, 0.25, 0.3) == 0 && BreakTick.scale(1, 0.25, 0.2) == 1, "stone: 1 XP a quarter of the time");
        check(BreakTick.share(0.25, true) == 0.6, "felled logs after the first give 60%");
        check(BreakTick.share(0.25, false) == 0.25, "ore and stone after the first still give 25%");
        check(BreakTick.share(1.0, true) == 1.0, "the first block of the tick is always full XP");
        System.out.println("BreakTickTest ok");
    }

    private static void check(boolean ok, String what) {
        if (!ok) { System.out.println("FAIL: " + what); System.exit(1); }
    }
}
