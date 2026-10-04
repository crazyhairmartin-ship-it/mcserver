package fotfskills.xp;

import net.puffish.skillsmod.api.experience.source.ExperienceSource;
import net.puffish.skillsmod.api.experience.source.ExperienceSourceDisposeContext;

/** fotfskills:break: XP for naturally generated blocks (BlockPerks skips player-placed ones). */
public record BreakSource(BreakRules rules) implements ExperienceSource {
    @Override
    public void dispose(ExperienceSourceDisposeContext context) {
    }
}
