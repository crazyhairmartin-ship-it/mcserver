package fotfskills;

import fotfskills.perk.ArsMana;
import fotfskills.perk.ArsPerks;
import fotfskills.perk.BlockPerks;
import fotfskills.perk.BreedingPerks;
import fotfskills.perk.CombatPerks;
import fotfskills.perk.CraftPerks;
import fotfskills.perk.FarmPerks;
import fotfskills.perk.FishingPerks;
import fotfskills.perk.FoodPerks;
import fotfskills.perk.ConditionalStats;
import fotfskills.perk.IronsMana;
import fotfskills.perk.IronsPerks;
import fotfskills.perk.Mana;
import fotfskills.perk.ItemPerks;
import fotfskills.perk.PerkReward;
import fotfskills.perk.OpacParties;
import fotfskills.perk.Parties;
import fotfskills.perk.PerkSync;
import fotfskills.perk.PetPerks;
import fotfskills.perk.RangePerks;
import fotfskills.perk.ShieldPerks;
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
        MinecraftForge.EVENT_BUS.register(new PetPerks());
        MinecraftForge.EVENT_BUS.register(new BreedingPerks());
        MinecraftForge.EVENT_BUS.register(new FarmPerks());
        MinecraftForge.EVENT_BUS.register(new FoodPerks());
        MinecraftForge.EVENT_BUS.register(new FishingPerks());
        MinecraftForge.EVENT_BUS.register(new CraftPerks());
        MinecraftForge.EVENT_BUS.register(new RangePerks());
        MinecraftForge.EVENT_BUS.register(new ShieldPerks());
        if (ModList.get().isLoaded("openpartiesandclaims")) {
            Parties.register(OpacParties::same);
        }
        MinecraftForge.EVENT_BUS.register(new ForgeXpEvents());
        if (ModList.get().isLoaded("ars_nouveau")) {
            MinecraftForge.EVENT_BUS.register(new ArsPerks());
            Mana.register(ArsMana::add);
            Mana.registerSpender(ArsMana::spend);
        }
        if (ModList.get().isLoaded("irons_spellbooks")) {
            MinecraftForge.EVENT_BUS.register(new IronsCastXp());
            MinecraftForge.EVENT_BUS.register(new IronsPerks());
            Mana.register(IronsMana::add);
            Mana.registerSpender(IronsMana::spend);
        }
    }
}
