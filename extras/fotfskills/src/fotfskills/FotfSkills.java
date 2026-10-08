package fotfskills;

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
        fotfskills.perk.ModItems.register(net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext.get().getModEventBus());
        fotfskills.world.RemovedBlocks.register(net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext.get().getModEventBus());
        PerkReward.register();
        fotfskills.perk.LevelUps.register();
        MinecraftForge.EVENT_BUS.register(new fotfskills.perk.FotfCommands());
        if (net.minecraftforge.fml.loading.FMLEnvironment.dist.isClient()) {
            fotfskills.client.ClientInit.register();
        }
        PerkSync.register();
        MinecraftForge.EVENT_BUS.register(new PerkSync());
        MinecraftForge.EVENT_BUS.register(new BlockPerks());
        MinecraftForge.EVENT_BUS.register(new ItemPerks());
        MinecraftForge.EVENT_BUS.register(new CombatPerks());
        MinecraftForge.EVENT_BUS.register(new WeaponPerks());
        MinecraftForge.EVENT_BUS.register(new ConditionalStats());
        MinecraftForge.EVENT_BUS.register(new fotfskills.perk.TotalLevel());
        if (ModList.get().isLoaded("grapplemod")) {
            MinecraftForge.EVENT_BUS.register(new fotfskills.perk.GrapplePerks());
        }
        MinecraftForge.EVENT_BUS.register(new PetPerks());
        MinecraftForge.EVENT_BUS.register(new fotfskills.pet.FairyCompanion());
        MinecraftForge.EVENT_BUS.register(new fotfskills.world.FlyerHeight());
        MinecraftForge.EVENT_BUS.register(new fotfskills.world.NamedPets());
        if (ModList.get().isLoaded("moremobvariants")) {
            MinecraftForge.EVENT_BUS.register(new fotfskills.world.WolfCoats());
        }
        MinecraftForge.EVENT_BUS.register(new BreedingPerks());
        MinecraftForge.EVENT_BUS.register(new fotfskills.pet.Ferality());
        MinecraftForge.EVENT_BUS.register(new fotfskills.world.RemovedBlocks());
        MinecraftForge.EVENT_BUS.register(new fotfskills.world.PlayerRules());
        if (ModList.get().isLoaded("ultimate_unicorn_mod")) {
            MinecraftForge.EVENT_BUS.register(new fotfskills.world.HorseSwim());
        }
        MinecraftForge.EVENT_BUS.register(new FarmPerks());
        MinecraftForge.EVENT_BUS.register(new FoodPerks());
        MinecraftForge.EVENT_BUS.register(new FishingPerks());
        MinecraftForge.EVENT_BUS.register(new CraftPerks());
        MinecraftForge.EVENT_BUS.register(new RangePerks());
        MinecraftForge.EVENT_BUS.register(new ShieldPerks());
        MinecraftForge.EVENT_BUS.register(new fotfskills.perk.StationBoost());
        MinecraftForge.EVENT_BUS.register(new fotfskills.perk.FeastPerks());
        MinecraftForge.EVENT_BUS.register(new fotfskills.perk.DrinkPerks());
        MinecraftForge.EVENT_BUS.register(new fotfskills.perk.SalvagePerks());
        MinecraftForge.EVENT_BUS.register(new fotfskills.perk.IrrigatorPerks());
        MinecraftForge.EVENT_BUS.register(new fotfskills.perk.SummonPerks());
        if (ModList.get().isLoaded("lilis_lucky_lures")) {
            MinecraftForge.EVENT_BUS.register(new fotfskills.perk.NetFishing());
            MinecraftForge.EVENT_BUS.register(new fotfskills.perk.TrapHaul());
        }
        if (ModList.get().isLoaded("butterflies")) {
            MinecraftForge.EVENT_BUS.register(new fotfskills.perk.NetReach());
        }
        if (ModList.get().isLoaded("irons_spellbooks")) {
            fotfskills.perk.SummonPerks.registerOwner(fotfskills.perk.ModSummons::irons);
        }
        if (ModList.get().isLoaded("openpartiesandclaims")) {
            Parties.register(OpacParties::same);
        }
        if (ModList.get().isLoaded("curios")) {
            MinecraftForge.EVENT_BUS.register(new fotfskills.compat.BackpackLantern());
            net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext.get().getModEventBus().addListener(
                    (net.minecraftforge.fml.event.lifecycle.FMLCommonSetupEvent e) -> fotfskills.compat.BackpackLantern.registerPredicate());
        }
        MinecraftForge.EVENT_BUS.register(new ForgeXpEvents());
        if (ModList.get().isLoaded("irons_spellbooks")) {
            MinecraftForge.EVENT_BUS.register(new IronsCastXp());
            MinecraftForge.EVENT_BUS.register(new IronsPerks());
            Mana.register(IronsMana::add);
            Mana.registerSpender(IronsMana::spend);
        }
    }
}
