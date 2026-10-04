package fotfskills.client;

import net.minecraftforge.common.MinecraftForge;

/** Client-only setup; only ever called on the physical client, so its client classes never load on a server. */
public final class ClientInit {
    private ClientInit() {
    }

    public static void register() {
        MinecraftForge.EVENT_BUS.register(new BuffsOverlay());
        MinecraftForge.EVENT_BUS.register(new DoubleJump());
        MinecraftForge.EVENT_BUS.register(new WeaponTooltips());
    }
}
