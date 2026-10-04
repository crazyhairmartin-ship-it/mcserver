package fotfskills.perk;

import java.util.HashSet;
import java.util.List;

/** Ingredient refunds only for real recipes: at least two different items (no compress/decompress loops). */
public final class Refund {
    private Refund() {
    }

    public static boolean eligible(List<String> ingredientIds) {
        return new HashSet<>(ingredientIds).size() >= 2;
    }
}
