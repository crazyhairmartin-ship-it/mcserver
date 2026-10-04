package fotfskills.perk;

import java.util.UUID;

/** Gentle Hand only rolls on a real failed tame: the animal's "failed" smoke (event 6) in the tick the player tried. */
public final class TameAttemptsTest {
    public static void main(String[] args) {
        TameAttempts attempts = new TameAttempts();
        UUID wolf = UUID.randomUUID(), cat = UUID.randomUUID(), dylan = UUID.randomUUID();
        attempts.tried(wolf, dylan, 100);
        check(attempts.failed(wolf, (byte) 7, 100) == null, "hearts (success) never roll");
        check(attempts.failed(cat, (byte) 6, 100) == null, "smoke on an animal nobody tried");
        check(dylan.equals(attempts.failed(wolf, (byte) 6, 100)), "smoke in the same tick: the player who tried");
        check(attempts.failed(wolf, (byte) 6, 100) == null, "one roll per attempt");
        attempts.tried(wolf, dylan, 200);
        check(attempts.failed(wolf, (byte) 6, 205) == null, "a stale attempt (leash, name tag, Q) never rolls later");
        System.out.println("TameAttemptsTest ok");
    }

    private static void check(boolean ok, String what) {
        if (!ok) { System.out.println("FAIL: " + what); System.exit(1); }
    }
}
