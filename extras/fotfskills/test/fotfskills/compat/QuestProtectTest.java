package fotfskills.compat;

import java.util.List;
import java.util.Set;

/** Quest puzzle blocks: which rules could cover a block, from the generated rule list. Run: sh test.sh */
public final class QuestProtectTest {
    public static void main(String[] args) {
        List<QuestProtect.Rule> rules = QuestProtect.parse("["
                + "{\"structures\": [\"mos:atlantis_tribune\"], \"blocks\": [\"minecraft:sea_lantern\"]},"
                + "{\"structures\": [\"#minecraft:village\", \"betterwitchhuts:witch_circle\"],"
                + " \"blocks\": [\"#minecraft:candles\", \"minecraft:lever\"]}]");
        check(rules.size() == 2, "two rules parsed");
        check(rules.get(1).structures().equals(List.of("#minecraft:village", "betterwitchhuts:witch_circle")),
                "structures kept in order, tags with #");

        Set<String> noTags = Set.of();
        check(QuestProtect.candidates(rules, "minecraft:sea_lantern", noTags::contains).size() == 1,
                "a listed block matches its rule");
        check(QuestProtect.candidates(rules, "minecraft:lever", noTags::contains).get(0) == rules.get(1),
                "the lever matches the second rule");
        check(QuestProtect.candidates(rules, "minecraft:stone", noTags::contains).isEmpty(),
                "other blocks match nothing");
        Set<String> candleTags = Set.of("minecraft:candles");
        check(QuestProtect.candidates(rules, "minecraft:red_candle", candleTags::contains).size() == 1,
                "a block in a listed tag matches");

        check(QuestProtect.parse("").isEmpty() && QuestProtect.parse("not json").isEmpty(),
                "bad or empty input gives no rules instead of failing");
        check(QuestProtect.parse("[{\"structures\": [], \"blocks\": [\"minecraft:lever\"]}]").isEmpty(),
                "a rule without structures is dropped (it would protect levers everywhere)");
        System.out.println("QuestProtectTest ok");
    }

    private static void check(boolean ok, String what) {
        if (!ok) { System.out.println("FAIL: " + what); System.exit(1); }
    }
}
