package fotfskills.xp;

import net.minecraft.server.level.ServerPlayer;
import net.puffish.skillsmod.api.SkillsAPI;
import net.puffish.skillsmod.api.experience.source.ExperienceSource;
import net.puffish.skillsmod.api.experience.source.ExperienceSourceDisposeContext;

/**
 * One configured fotfskills XP source: a kind ("cook", "tame", ...) and the factor from its data
 * (e.g. {"per_nutrition": 1.0}). Events call award(); every category with a source of that kind gets XP.
 */
public record AmountSource(String kind, double factor) implements ExperienceSource {
    public static void award(ServerPlayer player, String kind, double amount) {
        SkillsAPI.updateExperienceSources(player, AmountSource.class,
                source -> source.kind.equals(kind) ? scaled(amount, source.factor) : 0);
    }

    /** round(amount x factor), but at least 1 for any positive amount. */
    public static int scaled(double amount, double factor) {
        if (amount <= 0) {
            return 0;
        }
        return Math.max(1, (int) Math.round(amount * factor));
    }

    @Override
    public void dispose(ExperienceSourceDisposeContext context) {
    }
}
