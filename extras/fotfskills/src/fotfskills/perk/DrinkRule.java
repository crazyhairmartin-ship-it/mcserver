package fotfskills.perk;

/**
 * Brewer: an effect the drink added or refreshed (it now lasts longer than before the sip) is stretched by the bonus.
 * Returns the new duration, or -1 to leave the effect alone.
 */
public final class DrinkRule {
    private DrinkRule() {
    }

    public static int extended(int before, int after, double bonus) {
        if (bonus <= 0 || after <= before) {
            return -1;
        }
        return (int) Math.round(after * (1 + bonus));
    }
}
