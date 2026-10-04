package fotfskills.perk;

import java.util.List;

/** Pet Scavenging loot: what a pet may find and drop near its owner. Common 70%, uncommon 25%, rare 5%. */
public final class Scavenge {
    public static final List<String> COMMON = List.of("minecraft:bone", "minecraft:string", "minecraft:feather",
            "minecraft:leather", "minecraft:flint", "minecraft:stick", "minecraft:wheat_seeds", "minecraft:rabbit_hide");
    public static final List<String> UNCOMMON = List.of("minecraft:iron_nugget", "minecraft:gold_nugget", "minecraft:coal",
            "minecraft:slime_ball", "minecraft:honeycomb", "minecraft:amethyst_shard");
    public static final List<String> RARE = List.of("minecraft:emerald", "minecraft:diamond", "minecraft:name_tag",
            "minecraft:golden_apple");

    private Scavenge() {
    }

    public static String pick(double roll) {
        if (roll < 0.70) {
            return COMMON.get((int) (roll / 0.70 * COMMON.size()));
        }
        if (roll < 0.95) {
            return UNCOMMON.get((int) ((roll - 0.70) / 0.25 * UNCOMMON.size()));
        }
        return RARE.get(Math.min(RARE.size() - 1, (int) ((roll - 0.95) / 0.05 * RARE.size())));
    }
}
