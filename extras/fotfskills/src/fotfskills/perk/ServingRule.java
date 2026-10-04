package fotfskills.perk;

/**
 * Feast Maker: a block's serving was just taken when its "servings" went down by one, or its "bites" (Farmer's Delight,
 * vanilla cake) or "cuts" (Let's Do pies and cakes) went up by one.
 */
public final class ServingRule {
    private ServingRule() {
    }

    public static boolean taken(String property, int before, int after) {
        return ("servings".equals(property) && after == before - 1) || (("bites".equals(property) || "cuts".equals(property)) && after == before + 1);
    }
}
