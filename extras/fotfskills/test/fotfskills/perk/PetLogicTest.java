package fotfskills.perk;

/** Pet scavenging table and horse stat inheritance. Run: sh test.sh */
public final class PetLogicTest {
    public static void main(String[] args) {
        check(Scavenge.pick(0.0).equals("minecraft:bone"), "lowest roll is the first common item");
        check(Scavenge.COMMON.contains(Scavenge.pick(0.69)), "under 0.70 is common");
        check(Scavenge.UNCOMMON.contains(Scavenge.pick(0.80)), "0.70-0.95 is uncommon");
        check(Scavenge.RARE.contains(Scavenge.pick(0.99)), "top 5% is rare");

        check(Breeding.stat(20, 26, false, 30, 0) == 26, "better parent's stat");
        check(Math.abs(Breeding.stat(20, 26, true, 30, 0) - 27.3) < 1e-9, "bonus +5%");
        check(Breeding.stat(29, 30, true, 30, 0) == 30, "capped at the vanilla max");
        check(Math.abs(Breeding.stat(29, 30, true, 30, 0.1) - 31.5) < 1e-9, "Prized Stock lifts the cap 10%");
        System.out.println("PetLogicTest ok");
    }

    private static void check(boolean ok, String what) {
        if (!ok) { System.out.println("FAIL: " + what); System.exit(1); }
    }
}
