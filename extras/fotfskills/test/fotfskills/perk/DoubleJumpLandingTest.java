package fotfskills.perk;

import java.util.UUID;

/** After a double jump only the drop below the take-off height counts as a fall. Run: sh test.sh */
public final class DoubleJumpLandingTest {
    public static void main(String[] args) {
        UUID a = UUID.randomUUID();
        DoubleJumpLanding landing = new DoubleJumpLanding();

        landing.ground(a, 64);
        check(landing.fall(a, 3.8f, 64) == 3.8f, "no double jump: the fall counts as usual");

        landing.ground(a, 64);
        landing.jumped(a);
        check(landing.fall(a, 3.8f, 64) == 0, "full double jump back onto flat ground: no fall");
        check(landing.fall(a, 3.8f, 64) == 3.8f, "the allowance is used up by that landing");

        landing.ground(a, 64);
        landing.jumped(a);
        check(landing.fall(a, 13.5f, 54) == 10, "double jump off a 10-block drop: only the 10 blocks count");

        landing.ground(a, 64);
        landing.jumped(a);
        check(landing.fall(a, 2f, 66) == 0, "landing higher than take-off: no fall");

        landing.ground(a, 64);
        landing.jumped(a);
        check(landing.fall(a, 4f, 63.5f) == 0.5f, "half a block below take-off counts half a block");

        landing.jumped(a);
        landing.ground(a, 70);
        check(landing.fall(a, 5f, 64) == 5f, "touching ground clears the double jump");

        UUID b = UUID.randomUUID();
        landing.jumped(b);
        check(landing.fall(b, 4f, 64) == 4f, "no known take-off height: the fall counts as usual");
        System.out.println("DoubleJumpLandingTest ok");
    }

    private static void check(boolean ok, String what) {
        if (!ok) { System.out.println("FAIL: " + what); System.exit(1); }
    }
}
