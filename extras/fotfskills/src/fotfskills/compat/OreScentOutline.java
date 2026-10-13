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

    /** Outline colour by the ore inside (block id); first match wins, unknown ores stay white. */
    private static final String[] NAMES = {"ancient_debris", "quartz", "diamond", "emerald", "gold", "iron", "copper",
            "redstone", "lapis", "coal", "mithril"};
    private static final int[] COLOURS = {0xB040FF, 0xFFFFFF, 0x40E0F0, 0x30E060, 0xFFD020, 0xD8B898, 0xFF8C40,
            0xFF2020, 0x3050FF, 0x505050, 0x9EC8FF};

    public static int colour(String blockId) {
        String name = blockId.substring(blockId.indexOf(':') + 1);     // the block's name, not its mod ("irons_spellbooks")
        for (int i = 0; i < NAMES.length; i++) {
            if (name.contains(NAMES[i])) {
                return COLOURS[i];
            }
        }
        return 0xFFFFFF;
    }
}
