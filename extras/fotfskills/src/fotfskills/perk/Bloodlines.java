package fotfskills.perk;

import java.util.Map;
import java.util.Random;

/**
 * Bloodlines: the NBT that turns a vanilla baby into one of its rare looks (blue axolotl, pink or brown sheep, brown
 * panda or mooshroom, screaming goat, snow fox, salt-and-pepper or black-and-white rabbit, blue parrot, marked horse).
 * Empty for anything else, so modded animals keep their own genetics.
 */
public final class Bloodlines {
    private Bloodlines() {
    }

    public static Map<String, Object> rare(String entityId, Random random) {
        switch (entityId) {
            case "minecraft:axolotl":
                return Map.of("Variant", 4);
            case "minecraft:sheep":
                return Map.of("Color", random.nextBoolean() ? (byte) 6 : (byte) 12);
            case "minecraft:panda":
                return Map.of("MainGene", "brown", "HiddenGene", "brown");
            case "minecraft:mooshroom":
                return Map.of("Type", "brown");
            case "minecraft:goat":
                return Map.of("IsScreamingGoat", true);
            case "minecraft:fox":
                return Map.of("Type", "snow");
            case "minecraft:rabbit":
                return Map.of("RabbitType", random.nextBoolean() ? 3 : 5);
            case "minecraft:parrot":
                return Map.of("Variant", 3);
            case "minecraft:horse":
                return Map.of("Variant", random.nextInt(7) | (1 + random.nextInt(4)) << 8);
            default:
                return Map.of();
        }
    }
}
