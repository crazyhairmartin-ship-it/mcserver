package fotfars;

import java.util.Optional;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.network.NetworkDirection;
import net.minecraftforge.network.NetworkRegistry;
import net.minecraftforge.network.simple.SimpleChannel;

/**
 * Friends of the Forest tweaks for Ars Nouveau (both sides).
 *
 * - Storage Lectern: a creative-tab sort mode, and "move matching items" / "restock" side tabs (LecternDeposit).
 * - Bookwyrms wander around their lectern network instead of only hovering at chests (BookwyrmWanderGoal).
 *
 * Compiled against SRG-named Minecraft (see build.sh), so vanilla methods appear as m_XXXX_.
 */
@Mod(FotfArs.MODID)
public class FotfArs {
    public static final String MODID = "fotfars";

    private static final String PROTOCOL = "1";
    public static final SimpleChannel NETWORK = NetworkRegistry.newSimpleChannel(
            new ResourceLocation(MODID, "main"), () -> PROTOCOL, PROTOCOL::equals, PROTOCOL::equals);

    public FotfArs() {
        NETWORK.registerMessage(0, LecternDeposit.class, LecternDeposit::encode, LecternDeposit::decode,
                LecternDeposit::handle, Optional.of(NetworkDirection.PLAY_TO_SERVER));
    }
}
