package fotfskills.compat;

import java.util.Random;
import java.util.Set;
import java.util.UUID;

/**
 * Names for village waystones that describe their setting (Pinewall, Snowcap Rest, Redrock Bastion): a word for the
 * biome's character plus a place-word, picked by the waystone's id so the same waystone always gets the same name,
 * skipping names already in use. Pure logic; compat/VillageWaystones applies it.
 */
public final class WaystoneNames {
    public enum Category { COLD, MOUNTAIN, DRY, PINE, MUSHROOM, WETLAND, JUNGLE, COAST, DARK, FOREST, PLAINS }

    // checked in order: the first match wins (snowy slopes are cold before they're mountains)
    private static final String[][] KEYWORDS = {
            {"COLD", "snow", "frozen", "ice", "tundra", "glacier", "frost", "winter", "cold"},
            {"MUSHROOM", "mushroom", "fungal", "shroom"},
            {"DARK", "dark", "gloom", "dead", "ominous", "ashen", "bleak", "eerie"},
            {"MOUNTAIN", "mountain", "peak", "slope", "crag", "cliff", "alpine", "highland", "summit", "spire"},
            {"DRY", "desert", "dune", "mesa", "badlands", "outback", "wasteland", "steppe", "savanna", "scrub", "arid",
                    "sand", "dry"},
            {"PINE", "taiga", "pine", "boreal", "conifer", "spruce", "redwood", "fir"},
            {"WETLAND", "swamp", "marsh", "bayou", "mangrove", "fen", "bog", "wetland"},
            {"JUNGLE", "jungle", "rainforest", "tropic", "bamboo"},
            {"COAST", "beach", "coast", "shore", "ocean", "river", "lake", "sea", "reef"},
            {"FOREST", "forest", "wood", "grove", "maple", "birch", "oak", "cherry", "magnolia", "orchard"},
    };

    private static final String[][] FIRST = {
            /* COLD */ {"Frost", "Snow", "Rime", "Winter", "Hoar", "White", "Sleet", "Icewind", "Coldwater", "Snowcap"},
            /* MOUNTAIN */ {"High", "Crag", "Stone", "Eagle", "Cloud", "Ridge", "Scree", "Granite", "Skyward", "Windy"},
            /* DRY */ {"Sun", "Red", "Dust", "Sand", "Ochre", "Thorn", "Amber", "Dry", "Saltpan", "Sunbaked"},
            /* PINE */ {"Pine", "Fir", "Needle", "Spruce", "Timber", "Cone", "Resin", "Tall", "Evergreen", "Northwood"},
            /* MUSHROOM */ {"Spore", "Cap", "Mycel", "Shroom", "Puffball", "Morel", "Toadstool", "Gill", "Mould", "Truffle"},
            /* WETLAND */ {"Reed", "Mire", "Bog", "Fen", "Willow", "Mud", "Frog", "Rush", "Marsh", "Sedge"},
            /* JUNGLE */ {"Vine", "Liana", "Parrot", "Fern", "Canopy", "Orchid", "Monsoon", "Jade", "Banyan", "Cocoa"},
            /* COAST */ {"Salt", "Gull", "Tide", "Shell", "Driftwood", "Harbour", "Brine", "Seaspray", "Anchor", "Kelp"},
            /* DARK */ {"Shadow", "Gloom", "Raven", "Dusk", "Hollow", "Grim", "Black", "Murk", "Ashen", "Night"},
            /* FOREST */ {"Oak", "Birch", "Maple", "Elder", "Hazel", "Green", "Bramble", "Fernwood", "Rowan", "Acorn"},
            /* PLAINS */ {"Meadow", "Clover", "Barley", "Wheat", "Field", "Haystack", "Brook", "Daisy", "Lark", "Green"},
    };
    private static final String[] SECOND = {
            "hold", "wall", "fall", "mere", "haven", "stead", "watch", "crest", "ford", "brook", "field", "dale",
            "wick", "ton", "bury", "hollow", " Rest", " Reach", " Crossing", " Hill", " Green", " Well", " End", " Gate"};

    private WaystoneNames() {
    }

    public static Category category(String biomeId) {
        String path = biomeId.substring(biomeId.indexOf(':') + 1);
        for (String[] row : KEYWORDS) {
            for (int i = 1; i < row.length; i++) {
                if (path.contains(row[i])) {
                    return Category.valueOf(row[0]);
                }
            }
        }
        return Category.PLAINS;
    }

    /** A name for this waystone in this biome, stable for the waystone, never one of {@code taken}. */
    public static String name(String biomeId, UUID waystone, Set<String> taken) {
        String[] first = FIRST[category(biomeId).ordinal()];
        Random random = new Random(waystone.getMostSignificantBits() ^ waystone.getLeastSignificantBits());
        for (int attempt = 0; attempt < 200; attempt++) {
            String a = first[random.nextInt(first.length)];
            String b = SECOND[random.nextInt(SECOND.length)];
            String candidate = b.startsWith(" ") ? a + b : a + b.toLowerCase();
            if (!a.toLowerCase().endsWith(b.trim().toLowerCase()) && !taken.contains(candidate)) {
                return candidate;
            }
        }
        for (int n = 2; ; n++) {                             // every combination taken: number the first one
            String candidate = first[0] + SECOND[0] + " " + n;
            if (!taken.contains(candidate)) {
                return candidate;
            }
        }
    }
}
