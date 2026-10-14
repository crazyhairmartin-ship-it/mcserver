package fotfskills.compat;

import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import java.util.ArrayList;
import java.util.List;
import java.util.function.Predicate;

/**
 * Quest puzzle blocks (the quest book's "protect"): inside the listed structures, the listed blocks can't be broken,
 * blown up or pushed by pistons, so a puzzle can't be skipped by breaking it. Everything else there stays normal
 * survival. The rules come from the quest generator through KubeJS (quest_givers.js calls configure on every load);
 * the game side is QuestProtectHooks. Ids are "namespace:path"; a leading "#" means a tag.
 */
public final class QuestProtect {
    /** resetSeconds: blocks of this rule that players place inside the structure are cleared after this long (0: never). */
    public record Rule(List<String> structures, List<String> blocks, int resetSeconds) {}

    private static volatile List<Rule> rules = List.of();

    private QuestProtect() {}

    /** Called from KubeJS with the generated rules (a JSON array); replaces the current ones. */
    public static void configure(String json) {
        rules = parse(json);
    }

    public static List<Rule> rules() {
        return rules;
    }

    public static List<Rule> parse(String json) {
        List<Rule> out = new ArrayList<>();
        JsonElement root;
        try {
            root = JsonParser.parseString(json == null ? "" : json);
        } catch (RuntimeException e) {
            return List.of();
        }
        if (!root.isJsonArray()) {
            return List.of();
        }
        for (JsonElement el : root.getAsJsonArray()) {
            if (!el.isJsonObject()) {
                continue;
            }
            JsonObject o = el.getAsJsonObject();
            List<String> structures = strings(o.get("structures"));
            List<String> blocks = strings(o.get("blocks"));
            if (!structures.isEmpty() && !blocks.isEmpty()) {
                int reset = o.has("reset") && o.get("reset").isJsonPrimitive() ? Math.max(0, o.get("reset").getAsInt()) : 0;
                out.add(new Rule(List.copyOf(structures), List.copyOf(blocks), reset));
            }
        }
        return List.copyOf(out);
    }

    /** The rules whose blocks include this block (by id, or by a tag it's in). The structure check is left to the caller. */
    public static List<Rule> candidates(List<Rule> rules, String blockId, Predicate<String> inTag) {
        List<Rule> out = new ArrayList<>();
        for (Rule r : rules) {
            for (String b : r.blocks()) {
                if (b.startsWith("#") ? inTag.test(b.substring(1)) : b.equals(blockId)) {
                    out.add(r);
                    break;
                }
            }
        }
        return out;
    }

    private static List<String> strings(JsonElement el) {
        List<String> out = new ArrayList<>();
        if (el != null && el.isJsonArray()) {
            JsonArray a = el.getAsJsonArray();
            for (JsonElement s : a) {
                if (s.isJsonPrimitive()) {
                    out.add(s.getAsString());
                }
            }
        }
        return out;
    }
}
