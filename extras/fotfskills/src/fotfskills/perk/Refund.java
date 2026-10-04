package fotfskills.perk;

import java.util.HashSet;
import java.util.List;

/**
 * Ingredient refunds only for real recipes: at least two different items (no compress/decompress loops), and never
 * a stack that a recipe carries into its output (tools being modified, backpacks, shields: damageable, unstackable
 * or carrying NBT).
 */
public final class Refund {
    private Refund() {
    }

    public static boolean eligible(List<String> ingredientIds) {
        return new HashSet<>(ingredientIds).size() >= 2;
    }

    public static boolean refundableStack(boolean damageable, int maxStackSize, boolean hasTag) {
        return !damageable && maxStackSize > 1 && !hasTag;
    }
}
