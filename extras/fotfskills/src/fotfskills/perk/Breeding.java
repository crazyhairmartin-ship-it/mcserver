package fotfskills.perk;

/** Selective Breeding / Prized Stock: a foal gets the better parent's stat, maybe +5%, capped (Prized Stock lifts the cap). */
public final class Breeding {
    private Breeding() {
    }

    /** Prized Stock: the parents' breeding cooldown, cut by the perk's fraction but never below 30 seconds. */
    public static int cooldown(int vanilla, double cut) {
        return Math.max(600, (int) Math.round(vanilla * (1 - cut)));
    }

    public static double stat(double a, double b, boolean bonus, double vanillaMax, double prized) {
        double value = Math.max(a, b) * (bonus ? 1.05 : 1);
        return Math.min(value, vanillaMax * (1 + prized));
    }
}
