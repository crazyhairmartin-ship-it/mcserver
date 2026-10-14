package fotfskills.compat;

import java.util.List;

/** Protected areas around quest characters: parsing, inside checks, what stays allowed. Run: sh test.sh */
public final class QuestAreasTest {
    public static void main(String[] args) {
        List<QuestAreas.Area> areas = QuestAreas.parse("[{\"dimension\": \"minecraft:overworld\","
                + " \"min\": [3338, 61, -4136], \"max\": [3362, 83, -4112]},"
                + " {\"dimension\": \"minecraft:the_nether\", \"min\": [0, 0, 0], \"max\": [10, 10, 10]}]");
        check(areas.size() == 2, "two areas parsed");
        check(QuestAreas.inside(areas, "minecraft:overworld", 3350, 67, -4123), "Maren's spot is inside");
        check(QuestAreas.inside(areas, "minecraft:overworld", 3338, 61, -4136)
                && QuestAreas.inside(areas, "minecraft:overworld", 3362, 83, -4112), "edges count as inside");
        check(!QuestAreas.inside(areas, "minecraft:overworld", 3363, 67, -4123), "one block out is outside");
        check(!QuestAreas.inside(areas, "minecraft:overworld", 3350, 90, -4123), "far above is outside");
        check(!QuestAreas.inside(areas, "minecraft:the_nether", 3350, 67, -4123)
                && QuestAreas.inside(areas, "minecraft:the_nether", 5, 5, 5), "areas are per dimension");
        check(QuestAreas.parse("nope").isEmpty() && QuestAreas.parse("[{\"min\": [0,0,0]}]").isEmpty(),
                "bad input gives no areas");
        check(QuestAreas.parse("[{\"dimension\": \"d\", \"min\": [5, 5, 5], \"max\": [0, 0, 0]}]").get(0).min()[0] == 0,
                "min and max are put in order");
        System.out.println("QuestAreasTest ok");
    }

    private static void check(boolean ok, String what) {
        if (!ok) { System.out.println("FAIL: " + what); System.exit(1); }
    }
}
