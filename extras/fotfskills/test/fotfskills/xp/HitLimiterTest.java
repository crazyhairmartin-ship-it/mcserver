package fotfskills.xp;

import java.util.UUID;

/** Defense XP per attacker is capped per window, so caged mobs can't be farmed. Run: sh test.sh */
public final class HitLimiterTest {
    public static void main(String[] args) {
        HitLimiter limiter = new HitLimiter(30, 6000);
        UUID me = UUID.randomUUID(), zombie = UUID.randomUUID(), skeleton = UUID.randomUUID();
        check(limiter.grant(me, zombie, 20, 0) == 20, "first hits count in full");
        check(limiter.grant(me, zombie, 20, 100) == 10, "capped at 30 per attacker");
        check(limiter.grant(me, zombie, 5, 200) == 0, "nothing more in the window");
        check(limiter.grant(me, skeleton, 5, 200) == 5, "another attacker has its own cap");
        check(limiter.grant(me, zombie, 5, 6001) == 5, "a new window starts after 6000 ticks");
        check(limiter.grant(me, me, 5, 6001) == 0, "self-inflicted damage never counts");
        System.out.println("HitLimiterTest ok");
    }

    private static void check(boolean ok, String what) {
        if (!ok) { System.out.println("FAIL: " + what); System.exit(1); }
    }
}
