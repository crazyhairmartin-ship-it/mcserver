package fotfskills.perk;

import fotfskills.world.Marks;
import java.util.List;

/** Phase 2b review fixes: refundable stacks, bite time after Lure, and placed marks following pistons. */
public final class ReviewFixesTest {
    public static void main(String[] args) {
        check(Refund.refundableStack(false, 64, false), "plain ingredient refundable");
        check(!Refund.refundableStack(true, 1, true), "a tool being modified is never refunded");
        check(!Refund.refundableStack(false, 1, false), "unstackables (backpacks, shields) never refunded");
        check(!Refund.refundableStack(false, 64, true), "stacks with NBT never refunded");

        check(BiteTime.scale(300, 0.5) == 150, "wait halves");
        check(BiteTime.scale(0, 0.5) == 0, "Lure already made it 0: vanilla re-rolls, perk leaves it alone");
        check(BiteTime.scale(-50, 0.5) == -50, "negative after Lure untouched (perk never makes fish stop biting)");
        check(BiteTime.scale(1, 0.8) == 1, "never below 1 tick");
        check(BiteTime.scale(100, 0.95) == 20, "capped at 80% faster");

        Marks marks = new Marks();
        marks.mark(10);
        marks.mark(11);
        marks.move(List.of(10L, 11L), List.of(20L, 21L));
        check(!marks.contains(10) && !marks.contains(11), "old positions cleared");
        check(marks.contains(20) && marks.contains(21), "marks follow the pushed blocks");
        marks.mark(30);
        marks.move(List.of(30L, 31L), List.of(31L, 32L));
        check(!marks.contains(30) && marks.contains(31) && !marks.contains(32), "chain push: only the marked block's mark moves");
        System.out.println("ReviewFixesTest ok");
    }

    private static void check(boolean ok, String what) {
        if (!ok) { System.out.println("FAIL: " + what); System.exit(1); }
    }
}
