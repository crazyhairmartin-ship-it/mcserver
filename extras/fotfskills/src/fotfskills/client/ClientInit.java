package fotfskills.client;

import net.minecraftforge.common.MinecraftForge;

/** Client-only setup; only ever called on the physical client, so its client classes never load on a server. */
public final class ClientInit {
    private ClientInit() {
    }

    public static void register() {
        MinecraftForge.EVENT_BUS.register(new BuffsOverlay());
        MinecraftForge.EVENT_BUS.register(new DoubleJump());
        MinecraftForge.EVENT_BUS.register(new WeaponMasterCombo());
        MinecraftForge.EVENT_BUS.register(new WeaponTooltips());
        if (net.minecraftforge.fml.ModList.get().isLoaded("twilightforest")) {
            net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext.get().getModEventBus()
                    .addListener(BanisterCornerModels::onModifyBakingResult);
        }
        net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext.get().getModEventBus().addListener(DaleEarsLayer::onAddLayers);
        if (net.minecraftforge.fml.ModList.get().isLoaded("obscuras_storage")) {
            MinecraftForge.EVENT_BUS.register(new TerminalDepositButton());
        }
        if (net.minecraftforge.fml.ModList.get().isLoaded("moremobvariants")) {
            MinecraftForge.EVENT_BUS.register(new CustomCoats());
        }
    }
}
