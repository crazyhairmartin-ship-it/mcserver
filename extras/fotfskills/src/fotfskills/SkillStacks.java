package fotfskills;

import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import net.puffish.skillsmod.api.Skill;
import net.puffish.skillsmod.client.config.skill.ClientSkillConfig;
import net.puffish.skillsmod.client.data.ClientCategoryData;

/**
 * A node with ranks is several Pufferfish skills named {@code <node>_1 .. <node>_N} on the same tile
 * (tools/skills/make_skill_trees.py). Only one rank of a stack is drawn and clickable: the first one not unlocked
 * yet, or the last one once all are owned.
 */
public final class SkillStacks {
    /** Advancement-like window size, in GUI pixels (the screen is never bigger than the game window). */
    public static final int WINDOW_WIDTH = 280;
    public static final int WINDOW_HEIGHT = 230;

    private static final Pattern RANK = Pattern.compile("^(.+)_(\\d+)$");

    private SkillStacks() {
    }

    /** Owned and total ranks of the stack this skill belongs to, or null if it isn't a multi-rank stack. */
    public static int[] counter(ClientCategoryData data, ClientSkillConfig skill) {
        Matcher m = RANK.matcher(skill.id());
        if (!m.matches()) {
            return null;
        }
        Map<String, ClientSkillConfig> skills = data.getConfig().skills();
        int total = 0;
        int owned = 0;
        for (int i = 1; ; i++) {
            ClientSkillConfig rank = skills.get(m.group(1) + "_" + i);
            if (rank == null || rank.x() != skill.x() || rank.y() != skill.y()) {
                break;
            }
            total = i;
            if (data.getSkillState(rank) == Skill.State.UNLOCKED) {
                owned++;
            }
        }
        return total > 1 ? new int[] {owned, total} : null;
    }

    /** Whether this skill is the one rank of its stack that gets drawn and clicked. */
    public static boolean isShown(ClientCategoryData data, ClientSkillConfig skill) {
        int[] c = counter(data, skill);
        if (c == null) {
            return true;
        }
        int rank = Integer.parseInt(RANK.matcher(skill.id()).replaceAll("$2"));
        return rank == Math.min(c[0] + 1, c[1]);
    }
}
