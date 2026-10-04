package fotfskills.perk;

import java.util.UUID;

/** Phase 3c/3d review fixes: Book Saver only on a real break, level-up announcements only for new levels, Chef. */
public final class ReviewFixes3cdTest {
    public static void main(String[] args) {
        check(BookSaverRule.isBreak(true, 249, 250, false), "a tool at its last point of durability broke");
        check(!BookSaverRule.isBreak(true, 0, 250, false), "an undamaged sword put in an item frame is not a break");
        check(!BookSaverRule.isBreak(false, 0, 0, false), "throwing the last javelin is not a break");
        check(!BookSaverRule.isBreak(true, 250, 250, true), "gear enchanted by Enchanted Crafts never becomes a book");

        LevelGate gate = new LevelGate();
        UUID me = UUID.randomUUID();
        check(gate.announce(me, "mining", 3), "first level-up is announced");
        check(!gate.announce(me, "mining", 3), "a new point without a new level (tree reset, admin points) is quiet");
        check(gate.announce(me, "mining", 4), "the next level is announced");
        check(gate.announce(me, "fishing", 1), "each skill tracks its own level");

        check(FoodPerks.chefDuration(600, 0.5) == 900, "Chef stretches the food's own duration, not what is left");
        System.out.println("ReviewFixes3cdTest ok");
    }

    private static void check(boolean ok, String what) {
        if (!ok) { System.out.println("FAIL: " + what); System.exit(1); }
    }
}
