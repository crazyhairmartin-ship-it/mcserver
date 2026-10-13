package fotfskills.compat;

/** Ore Scenting outlines are coloured by the ore inside. Run: sh test.sh */
public final class OreScentColourTest {
    public static void main(String[] args) {
        check(OreScentOutline.colour("minecraft:ancient_debris") == 0xB040FF, "ancient debris: strong purple");
        check(OreScentOutline.colour("minecraft:nether_quartz_ore") == 0xFFFFFF, "quartz stays white, clear of debris");
        check(OreScentOutline.colour("minecraft:deepslate_diamond_ore") == 0x40E0F0, "diamond (deepslate too): cyan");
        check(OreScentOutline.colour("minecraft:nether_gold_ore") == 0xFFD020, "nether gold: yellow like gold");
        check(OreScentOutline.colour("minecraft:deepslate_redstone_ore") == 0xFF2020, "redstone: red");
        check(OreScentOutline.colour("irons_spellbooks:mithril_ore") == 0x9EC8FF, "mithril: silvery blue");
        check(OreScentOutline.colour("somemod:tin_ore") == 0xFFFFFF, "unknown ores: white");
        System.out.println("OreScentColourTest ok");
    }

    private static void check(boolean ok, String what) {
        if (!ok) { System.out.println("FAIL: " + what); System.exit(1); }
    }
}
