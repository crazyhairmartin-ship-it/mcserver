package fotfskills.perk;

/** Phase 3a review fixes: one counted swing per tick (sweeps), and which projectiles count as arrows or thrown weapons. */
public final class ReviewFixes3aTest {
    public static void main(String[] args) {
        SwingGate gate = new SwingGate();
        check(gate.first(100), "the main target of a swing is the first hit this tick");
        check(!gate.first(100), "sweep targets in the same tick are not");
        check(gate.first(101), "the next tick's swing counts again");

        check(Projectiles.kind(true, true, false) == Projectiles.Kind.ARROW, "an arrow");
        check(Projectiles.kind(true, false, true) == Projectiles.Kind.THROWN, "a trident or javelin");
        check(Projectiles.kind(false, false, true) == Projectiles.Kind.THROWN, "a thrown knife item projectile");
        check(Projectiles.kind(false, false, false) == Projectiles.Kind.OTHER, "spells, pearls, bobbers, snowballs");
        check(Projectiles.kind(true, false, false) == Projectiles.Kind.OTHER, "a modded arrow-like spell bolt");
        System.out.println("ReviewFixes3aTest ok");
    }

    private static void check(boolean ok, String what) {
        if (!ok) { System.out.println("FAIL: " + what); System.exit(1); }
    }
}
