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
 * One player's skills for the character screen: level, XP toward the next level, points, and the nodes they own (named
 * from the skill tree config). Built on the server when the screen asks for it.
 */
public record SkillProfile(List<Entry> skills, int totalLevel) {
    public record Entry(String id, String name, int level, int current, int required, int spent, int points, List<String> perks) {
    }

    private static final Map<String, Map<String, String>> TITLES = new HashMap<>();
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
            Map<String, Integer> ranks = new LinkedHashMap<>();
            Map<String, String> titles = titles(id);
            category.streamUnlockedSkills(player).forEach(skill -> {
                String title = titles.get(skill.getId());
                if (title != null && !title.startsWith("Tier ") && !title.equals("OR")) {
                    ranks.merge(title, 1, Integer::sum);
                }
            });
            List<String> perks = new ArrayList<>();
            ranks.forEach((title, n) -> perks.add(n > 1 ? title + " x" + n : title));
            skills.add(new Entry(id, LevelUps.displayName(id), level, current, required, category.getSpentPoints(player),
                    category.getPointsTotal(player), perks));
            total += level;
        }
        return new SkillProfile(skills, total);
    }

    /** skill id -> node title, from config/puffish_skills/categories/<tree>/{skills,definitions}.json */
    private static Map<String, String> titles(String tree) {
        return TITLES.computeIfAbsent(tree, t -> {
            Map<String, String> out = new HashMap<>();
            Path dir = FMLPaths.CONFIGDIR.get().resolve("puffish_skills").resolve("categories").resolve(t);
            try (Reader skills = Files.newBufferedReader(dir.resolve("skills.json"));
                 Reader defs = Files.newBufferedReader(dir.resolve("definitions.json"))) {
                JsonObject skillJson = JsonParser.parseReader(skills).getAsJsonObject();
                JsonObject defJson = JsonParser.parseReader(defs).getAsJsonObject();
                for (String sid : skillJson.keySet()) {
                    String def = skillJson.getAsJsonObject(sid).get("definition").getAsString();
                    if (defJson.has(def)) {
                        out.put(sid, defJson.getAsJsonObject(def).get("title").getAsString());
                    }
                }
            } catch (Exception ignored) {
                // no config: nodes show without names
            }
            return out;
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
            e.perks.forEach(buf::m_130070_);
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
            List<String> perks = new ArrayList<>();
            for (int j = 0; j < p; j++) {
                perks.add(buf.m_130277_());
            }
            skills.add(new Entry(id, name, level, current, required, spent, points, perks));
        }
        return new SkillProfile(skills, total);
    }
}
