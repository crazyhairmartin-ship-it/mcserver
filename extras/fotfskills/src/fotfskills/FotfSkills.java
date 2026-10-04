package fotfskills;

import fotfskills.perk.PerkReward;
import fotfskills.perk.PerkSync;
import fotfskills.xp.ForgeXpEvents;
import fotfskills.xp.IronsCastXp;
import fotfskills.xp.XpSources;
import net.minecraftforge.common.MinecraftForge;
import net.minecraftforge.fml.ModList;
import net.minecraftforge.fml.common.Mod;

/** FOTF Skills: client skill-window tweaks (mixins) plus the custom XP sources for the skill trees. */
@Mod("fotfskills")
public final class FotfSkills {
    public FotfSkills() {
        XpSources.register();
        PerkReward.register();
        PerkSync.register();
        MinecraftForge.EVENT_BUS.register(new PerkSync());
        MinecraftForge.EVENT_BUS.register(new ForgeXpEvents());
        if (ModList.get().isLoaded("irons_spellbooks")) {
            MinecraftForge.EVENT_BUS.register(new IronsCastXp());
        }
    }
}
