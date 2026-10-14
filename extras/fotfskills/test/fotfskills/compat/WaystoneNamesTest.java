package fotfskills.compat;

import java.util.HashSet;
import java.util.Set;
import java.util.UUID;

/** Village waystones named after their setting. Run: sh test.sh */
public final class WaystoneNamesTest {
    public static void main(String[] args) {
        check(WaystoneNames.category("regions_unexplored:frozen_tundra") == WaystoneNames.Category.COLD, "tundra is cold");
        check(WaystoneNames.category("minecraft:snowy_slopes") == WaystoneNames.Category.COLD, "snowy slopes: snow wins over slopes");
        check(WaystoneNames.category("biomesoplenty:jade_cliffs") == WaystoneNames.Category.MOUNTAIN, "cliffs are mountains");
        check(WaystoneNames.category("regions_unexplored:boreal_taiga") == WaystoneNames.Category.PINE, "taiga is pine");
        check(WaystoneNames.category("biomesoplenty:wasteland_steppe") == WaystoneNames.Category.DRY, "steppe is dry");
        check(WaystoneNames.category("minecraft:mushroom_fields") == WaystoneNames.Category.MUSHROOM, "mushroom");
        check(WaystoneNames.category("minecraft:dark_forest") == WaystoneNames.Category.DARK, "dark forest is dark, not forest");
        check(WaystoneNames.category("regions_unexplored:magnolia_woodland") == WaystoneNames.Category.FOREST, "woodland is forest");
        check(WaystoneNames.category("minecraft:plains") == WaystoneNames.Category.PLAINS, "plains");
        check(WaystoneNames.category("somemod:strange_place") == WaystoneNames.Category.PLAINS, "unknown biomes: plains words");

        UUID id = UUID.fromString("00000000-0000-0000-0000-000000000042");
        String a = WaystoneNames.name("minecraft:taiga", id, new HashSet<>());
        String b = WaystoneNames.name("minecraft:taiga", id, new HashSet<>());
        check(a.equals(b), "the same waystone always gets the same name: " + a + " / " + b);
        check(!a.isBlank() && Character.isUpperCase(a.charAt(0)), "a capitalised name: " + a);

        Set<String> taken = new HashSet<>();
        for (int i = 0; i < 200; i++) {
            String n = WaystoneNames.name("minecraft:desert", new UUID(7, i), taken);
            check(taken.add(n), "never repeats a name already in use: " + n);
        }
        check(!WaystoneNames.name("minecraft:taiga", id, Set.of(a)).equals(a), "a taken name is skipped");
        System.out.println("WaystoneNamesTest ok");
    }

    private static void check(boolean ok, String what) {
        if (!ok) { System.out.println("FAIL: " + what); System.exit(1); }
    }
}
