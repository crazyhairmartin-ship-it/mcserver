package fotfskills.perk;

/**
 * Book Saver pays only for a real durability break: a damageable item at (or one point from) its maximum damage.
 * PlayerDestroyItemEvent also fires when a stack simply empties (item frames, allays, the last thrown javelin), and
 * gear enchanted by Enchanted Crafts never turns into books (no cheap-book loop).
 */
public final class BookSaverRule {
    private BookSaverRule() {
    }

    public static boolean isBreak(boolean damageable, int damage, int maxDamage, boolean perkEnchanted) {
        return damageable && maxDamage > 0 && damage >= maxDamage - 1 && !perkEnchanted;
    }
}
