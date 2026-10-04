package fotfskills.perk;

/** Feast Maker: a block's serving was just taken when its "servings" went down by one or its "bites" up by one. */
public final class ServingRule {
    private ServingRule() {
    }

    public static boolean taken(String property, int before, int after) {
        return ("servings".equals(property) && after == before - 1) || ("bites".equals(property) && after == before + 1);
    }
}
