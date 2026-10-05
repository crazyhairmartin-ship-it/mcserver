package fotfskills.xp;

import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import java.util.ArrayList;
import java.util.List;

/** Ordered XP rules for broken blocks: {"rules": [{"block": "#tag" | "ns:id", "mature_crop": bool, "experience": n}]}. */
public final class BreakRules {
    public interface Facts {
        String id();

        boolean hasTag(String tag);

        boolean matureCrop();

        /** Fully grown for any plant: no "age" property, or that age at its maximum (cocoa, berry bushes, wild crops). */
        default boolean mature() {
            return true;
        }
    }

    private record Rule(String block, boolean matureCrop, boolean mature, int experience) {
        boolean matches(Facts facts) {
            if (matureCrop && !facts.matureCrop()) {
                return false;
            }
            if (mature && !facts.mature()) {
                return false;
            }
            if (block == null) {
                return true;
            }
            return block.startsWith("#") ? facts.hasTag(block.substring(1)) : block.equals(facts.id());
        }
    }

    private final List<Rule> rules;

    private BreakRules(List<Rule> rules) {
        this.rules = rules;
    }

    public static BreakRules parse(JsonObject data) {
        List<Rule> rules = new ArrayList<>();
        for (JsonElement element : data.getAsJsonArray("rules")) {
            JsonObject rule = element.getAsJsonObject();
            rules.add(new Rule(rule.has("block") ? rule.get("block").getAsString() : null,
                    rule.has("mature_crop") && rule.get("mature_crop").getAsBoolean(),
                    rule.has("mature") && rule.get("mature").getAsBoolean(),
                    rule.get("experience").getAsInt()));
        }
        return new BreakRules(rules);
    }

    public int experience(Facts facts) {
        for (Rule rule : rules) {
            if (rule.matches(facts)) {
                return rule.experience;
            }
        }
        return 0;
    }
}
