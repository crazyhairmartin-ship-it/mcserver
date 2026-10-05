package fotfskills.perk;

import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import java.io.Reader;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.fml.loading.FMLPaths;
import net.puffish.skillsmod.api.Category;
import net.puffish.skillsmod.api.SkillsAPI;

/**
 * One player's skills for the character screen: level, XP toward the next level, points, and the nodes they own (title,
 * ranks owned out of the node's total, and what those ranks do, from the skill tree config). Built on the server when
 * the screen asks for it.
 */
public record SkillProfile(List<Entry> skills, int totalLevel) {
    public record Entry(String id, String name, int level, int current, int required, int spent, int points, List<Node> perks) {
    }

    public record Node(String title, int rank, int maxRank, String description) {
    }

    /** One node definition from the config: its title, description, and rank number (the _N suffix, 1 if none). */
    private record Def(String title, String description, int rank) {
    }

    /** Per tree: skill id -> definition, and title -> how many ranks the node has. */
    private record Tree(Map<String, Def> skills, Map<String, Integer> maxRanks) {
    }

    private static final Map<String, Tree> TREES = new HashMap<>();
    /** Client side: the last profile the server sent (the character screen reads it). */
    public static volatile SkillProfile latest;

    public static SkillProfile of(ServerPlayer player) {
        List<Entry> skills = new ArrayList<>();
        int total = 0;
        for (Category category : SkillsAPI.streamCategories().toList()) {
            String id = category.getId().m_135815_();
            int level = category.getExperience().map(e -> e.getLevel(player)).orElse(0);
            int current = category.getExperience().map(e -> e.getCurrent(player)).orElse(0);
            int required = category.getExperience().map(e -> e.getRequired(player, level)).orElse(0);
            Tree tree = tree(id);
            Map<String, Integer> ranks = new LinkedHashMap<>();
            Map<String, Def> best = new HashMap<>();
            category.streamUnlockedSkills(player).forEach(skill -> {
                Def def = tree.skills().get(skill.getId());
                if (def != null && !def.title().startsWith("Tier ") && !def.title().equals("OR")) {
                    ranks.merge(def.title(), 1, Integer::sum);
                    best.merge(def.title(), def, (a, b) -> b.rank() > a.rank() ? b : a);   // descriptions are cumulative
                }
            });
            List<Node> perks = new ArrayList<>();
            ranks.forEach((title, n) -> perks.add(new Node(title, n, Math.max(n, tree.maxRanks().getOrDefault(title, n)),
                    best.get(title).description())));
            skills.add(new Entry(id, LevelUps.displayName(id), level, current, required, category.getSpentPoints(player),
                    category.getPointsTotal(player), perks));
            total += level;
        }
        return new SkillProfile(skills, total);
    }

    /** From config/puffish_skills/categories/<tree>/{skills,definitions}.json */
    private static Tree tree(String tree) {
        return TREES.computeIfAbsent(tree, t -> {
            Map<String, Def> out = new HashMap<>();
            Map<String, Integer> maxRanks = new HashMap<>();
            Path dir = FMLPaths.CONFIGDIR.get().resolve("puffish_skills").resolve("categories").resolve(t);
            try (Reader skills = Files.newBufferedReader(dir.resolve("skills.json"));
                 Reader defs = Files.newBufferedReader(dir.resolve("definitions.json"))) {
                JsonObject skillJson = JsonParser.parseReader(skills).getAsJsonObject();
                JsonObject defJson = JsonParser.parseReader(defs).getAsJsonObject();
                for (String key : defJson.keySet()) {
                    JsonObject d = defJson.getAsJsonObject(key);
                    maxRanks.merge(d.get("title").getAsString(), 1, Integer::sum);
                }
                for (String sid : skillJson.keySet()) {
                    String key = skillJson.getAsJsonObject(sid).get("definition").getAsString();
                    if (defJson.has(key)) {
                        JsonObject d = defJson.getAsJsonObject(key);
                        java.util.regex.Matcher m = java.util.regex.Pattern.compile("_(\\d+)$").matcher(key);
                        out.put(sid, new Def(d.get("title").getAsString(),
                                d.has("description") ? d.get("description").getAsString() : "", m.find() ? Integer.parseInt(m.group(1)) : 1));
                    }
                }
            } catch (Exception ignored) {
                // no config: nodes show without names
            }
            return new Tree(out, maxRanks);
        });
    }

    public void encode(FriendlyByteBuf buf) {
        buf.m_130130_(totalLevel);
        buf.m_130130_(skills.size());
        for (Entry e : skills) {
            buf.m_130070_(e.id);
            buf.m_130070_(e.name);
            buf.m_130130_(e.level);
            buf.m_130130_(e.current);
            buf.m_130130_(e.required);
            buf.m_130130_(e.spent);
            buf.m_130130_(e.points);
            buf.m_130130_(e.perks.size());
            for (Node node : e.perks) {
                buf.m_130070_(node.title);
                buf.m_130130_(node.rank);
                buf.m_130130_(node.maxRank);
                buf.m_130070_(node.description);
            }
        }
    }

    public static SkillProfile decode(FriendlyByteBuf buf) {
        int total = buf.m_130242_();
        int n = buf.m_130242_();
        List<Entry> skills = new ArrayList<>();
        for (int i = 0; i < n; i++) {
            String id = buf.m_130277_();
            String name = buf.m_130277_();
            int level = buf.m_130242_(), current = buf.m_130242_(), required = buf.m_130242_();
            int spent = buf.m_130242_(), points = buf.m_130242_();
            int p = buf.m_130242_();
            List<Node> perks = new ArrayList<>();
            for (int j = 0; j < p; j++) {
                perks.add(new Node(buf.m_130277_(), buf.m_130242_(), buf.m_130242_(), buf.m_130277_()));
            }
            skills.add(new Entry(id, name, level, current, required, spent, points, perks));
        }
        return new SkillProfile(skills, total);
    }
}
