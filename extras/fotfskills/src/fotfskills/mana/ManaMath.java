package fotfskills.mana;

/** Shared mana conversions: Ars's max and regen bonuses expressed as Iron's max mana and mana regen. */
public final class ManaMath {
    private ManaMath() {
    }

    /** What Ars would give above its own base max mana (glyphs, book tier, gear); never negative. */
    public static int maxBonus(int arsMax, int arsBase) {
        return Math.max(0, arsMax - arsBase);
    }

    /**
     * Iron's regen stat bonus giving the same extra mana per second as Ars's regen above its base. Iron's regen adds
     * max x 0.01 x regen x multiplier every 10 ticks, i.e. max x 0.02 x regen x multiplier per second.
     */
    public static double regenBonus(double arsRegenPerSecond, double arsBaseRegen, double ironsMax, double multiplier) {
        double extra = arsRegenPerSecond - arsBaseRegen;
        double perRegenPoint = ironsMax * 0.02 * multiplier;
        if (extra <= 0 || perRegenPoint <= 0) {
            return 0;
        }
        return extra / perRegenPoint;
    }
}
