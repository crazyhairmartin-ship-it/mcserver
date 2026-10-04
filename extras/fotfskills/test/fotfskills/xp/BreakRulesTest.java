package fotfskills.xp;

import com.google.gson.JsonParser;
import java.util.Set;

/** First matching rule wins; tags start with '#'; mature_crop needs a fully grown crop. Run: sh test.sh */
public final class BreakRulesTest {
    record Facts(String id, Set<String> tags, boolean matureCrop) implements BreakRules.Facts {
        public boolean hasTag(String tag) { return tags.contains(tag); }
    }

    public static void main(String[] args) {
        BreakRules rules = BreakRules.parse(JsonParser.parseString("""
            {"rules": [
              {"block": "#forge:ores/diamond", "experience": 20},
              {"block": "#forge:ores", "experience": 6},
              {"block": "minecraft:stone", "experience": 1},
              {"mature_crop": true, "experience": 3}
            ]}""").getAsJsonObject());
        check(rules.experience(new Facts("minecraft:diamond_ore", Set.of("forge:ores", "forge:ores/diamond"), false)) == 20, "diamond first");
        check(rules.experience(new Facts("minecraft:iron_ore", Set.of("forge:ores"), false)) == 6, "plain ore");
        check(rules.experience(new Facts("minecraft:stone", Set.of(), false)) == 1, "block id");
        check(rules.experience(new Facts("minecraft:wheat", Set.of("minecraft:crops"), true)) == 3, "grown crop");
        check(rules.experience(new Facts("minecraft:wheat", Set.of("minecraft:crops"), false)) == 0, "unripe crop");
        check(rules.experience(new Facts("minecraft:dirt", Set.of(), false)) == 0, "no rule");
        System.out.println("BreakRulesTest ok");
    }

    private static void check(boolean ok, String what) {
        if (!ok) { System.out.println("FAIL: " + what); System.exit(1); }
    }
}
