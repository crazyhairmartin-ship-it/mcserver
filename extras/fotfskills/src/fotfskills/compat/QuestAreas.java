package fotfskills.compat;

import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import java.util.ArrayList;
import java.util.List;

/**
 * Protected areas: boxes around the quest characters' homes (built by the quest generator from
 * tools/quests/src/npc_positions.json) where survival players can't break or place blocks, and that explosions and
 * pistons leave alone. Using things (doors, chests, waystones, mailboxes, chairs, trading) still works, crops can still
 * be harvested and replanted, and ops are never stopped. Game side: QuestProtectHooks.
 */
public final class QuestAreas {
    public record Area(String dimension, int[] min, int[] max) {}

    private static volatile List<Area> areas = List.of();
    /** Per player (UUID): blocks ("id" or "#tag") their open quest build steps let them place in protected areas. */
    private static final java.util.Map<String, List<String>> ALLOWED = new java.util.concurrent.ConcurrentHashMap<>();

    private QuestAreas() {}

    /** Called from KubeJS with the generated areas (a JSON array); replaces the current ones. */
    public static void configure(String json) {
        areas = parse(json);
    }

    public static List<Area> areas() {
        return areas;
    }

    /** Called from KubeJS (quest_npcs.js) every few seconds with the blocks a player's open build steps need. */
    public static void setAllowed(String player, List<String> keys) {
        if (keys == null || keys.isEmpty()) {
            ALLOWED.remove(player);
        } else {
            ALLOWED.put(player, List.copyOf(keys));
        }
    }

    public static List<String> allowed(String player) {
        return ALLOWED.getOrDefault(player, List.of());
    }

    public static boolean inside(List<Area> list, String dimension, int x, int y, int z) {
        for (Area a : list) {
            if (a.dimension().equals(dimension) && x >= a.min()[0] && x <= a.max()[0] && y >= a.min()[1]
                    && y <= a.max()[1] && z >= a.min()[2] && z <= a.max()[2]) {
                return true;
            }
        }
        return false;
    }

    public static List<Area> parse(String json) {
        JsonElement root;
        try {
            root = JsonParser.parseString(json == null ? "" : json);
        } catch (RuntimeException e) {
            return List.of();
        }
        if (!root.isJsonArray()) {
            return List.of();
        }
        List<Area> out = new ArrayList<>();
        for (JsonElement el : root.getAsJsonArray()) {
            if (!el.isJsonObject()) {
                continue;
            }
            JsonObject o = el.getAsJsonObject();
            int[] a = triple(o.get("min")), b = triple(o.get("max"));
            if (!o.has("dimension") || a == null || b == null) {
                continue;
            }
            int[] min = {Math.min(a[0], b[0]), Math.min(a[1], b[1]), Math.min(a[2], b[2])};
            int[] max = {Math.max(a[0], b[0]), Math.max(a[1], b[1]), Math.max(a[2], b[2])};
            out.add(new Area(o.get("dimension").getAsString(), min, max));
        }
        return List.copyOf(out);
    }

    private static int[] triple(JsonElement el) {
        if (el == null || !el.isJsonArray()) {
            return null;
        }
        JsonArray a = el.getAsJsonArray();
        if (a.size() != 3) {
            return null;
        }
        return new int[] {a.get(0).getAsInt(), a.get(1).getAsInt(), a.get(2).getAsInt()};
    }
}
