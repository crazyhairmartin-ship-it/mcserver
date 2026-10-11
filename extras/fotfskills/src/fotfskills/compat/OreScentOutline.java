package fotfskills.compat;

/**
 * Domestication Innovation's Ore Scenting outlines ore for 50 ticks per enchantment level; ours last half as long again
 * (3.75 / 7.5 / 11.25 s) so there's time to look round for them. Applied by mixin/OreScentOutlineMixin.
 */
public final class OreScentOutline {
    private OreScentOutline() {
    }

    public static int lifespan(int ticks) {
        return ticks * 3 / 2;
    }
}
