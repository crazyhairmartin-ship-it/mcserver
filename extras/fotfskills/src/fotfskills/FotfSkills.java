package fotfskills;

import fotfskills.perk.ArsMana;
import fotfskills.perk.ArsPerks;
import fotfskills.perk.BlockPerks;
import fotfskills.perk.CombatPerks;
import fotfskills.perk.ConditionalStats;
import fotfskills.perk.IronsMana;
import fotfskills.perk.IronsPerks;
import fotfskills.perk.Mana;
import fotfskills.perk.ItemPerks;
import fotfskills.perk.PerkReward;
import fotfskills.perk.PerkSync;
import fotfskills.perk.WeaponPerks;
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
        MinecraftForge.EVENT_BUS.register(new BlockPerks());
        MinecraftForge.EVENT_BUS.register(new ItemPerks());
        MinecraftForge.EVENT_BUS.register(new CombatPerks());
        MinecraftForge.EVENT_BUS.register(new WeaponPerks());
        MinecraftForge.EVENT_BUS.register(new ConditionalStats());
        MinecraftForge.EVENT_BUS.register(new ForgeXpEvents());
        if (ModList.get().isLoaded("ars_nouveau")) {
            MinecraftForge.EVENT_BUS.register(new ArsPerks());
            Mana.register(ArsMana::add);
        }
        if (ModList.get().isLoaded("irons_spellbooks")) {
            MinecraftForge.EVENT_BUS.register(new IronsCastXp());
            MinecraftForge.EVENT_BUS.register(new IronsPerks());
            Mana.register(IronsMana::add);
        }
    }
}
