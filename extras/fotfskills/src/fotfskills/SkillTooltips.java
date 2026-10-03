package fotfskills;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import net.minecraft.ChatFormatting;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.components.Tooltip;
import net.minecraft.network.chat.Component;
import net.minecraft.util.FormattedCharSequence;
import net.puffish.skillsmod.api.Skill;
import net.puffish.skillsmod.client.config.skill.ClientSkillConfig;
import net.puffish.skillsmod.client.config.skill.ClientSkillDefinitionConfig;
import net.puffish.skillsmod.client.data.ClientCategoryData;

/**
 * Tooltip for a node tile: its name, the effect of the ranks you own (white), the next rank's effect (grey, "Next:")
 * and its extra line (choice partner / prerequisite, aqua). Each rank's definition description is that rank's
 * effect (tools/skills/make_skill_trees.py); the tier numeral and OR tiles keep Pufferfish's own tooltip.
 */
public final class SkillTooltips {
    private SkillTooltips() {
    }

    /** Tooltip lines for this skill, or null to keep Pufferfish's tooltip. */
    public static List<FormattedCharSequence> build(Minecraft minecraft, ClientCategoryData data, ClientSkillConfig skill) {
        if (skill.id().startsWith("tier_")) {
            return null;
        }
        Map<String, ClientSkillDefinitionConfig> definitions = data.getConfig().definitions();
        Map<String, ClientSkillConfig> skills = data.getConfig().skills();
        int[] counter = SkillStacks.counter(data, skill);
        int owned;
        int total;
        String base = skill.id().replaceAll("_\\d+$", "");
        if (counter != null) {
            owned = counter[0];
            total = counter[1];
        } else {
            owned = data.getSkillState(skill) == Skill.State.UNLOCKED ? 1 : 0;
            total = 1;
        }
        ClientSkillDefinitionConfig shown = definitions.get(skill.definitionId());
        ClientSkillDefinitionConfig current = owned > 0 ? rank(definitions, skills, base, owned, skill) : null;
        ClientSkillDefinitionConfig next = owned < total ? rank(definitions, skills, base, owned + 1, skill) : null;

        List<FormattedCharSequence> lines = new ArrayList<>();
        lines.add(shown.title().m_7532_());
        if (current != null) {
            lines.addAll(Tooltip.m_257868_(minecraft, current.description().m_6881_().m_130940_(ChatFormatting.WHITE)));
        }
        if (next != null) {
            boolean sameText = current != null && current.description().getString().equals(next.description().getString());
            Component nextText = sameText ? Component.m_237113_("stronger") : next.description();
            lines.addAll(Tooltip.m_257868_(minecraft,
                    Component.m_237113_("Next: ").m_7220_(nextText).m_130940_(ChatFormatting.GRAY)));
        }
        String extra = shown.extraDescription().getString();
        if (!extra.isEmpty()) {
            lines.addAll(Tooltip.m_257868_(minecraft, Component.m_237113_(extra).m_130940_(ChatFormatting.DARK_AQUA)));
        }
        return lines;
    }

    private static ClientSkillDefinitionConfig rank(Map<String, ClientSkillDefinitionConfig> definitions,
                                                    Map<String, ClientSkillConfig> skills, String base, int rank,
                                                    ClientSkillConfig fallback) {
        ClientSkillConfig skill = skills.getOrDefault(base + "_" + rank, fallback);
        return definitions.get(skill.definitionId());
    }
}
