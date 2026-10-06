package fotfretrogen;

import net.minecraftforge.common.MinecraftForge;
import net.minecraftforge.fml.common.Mod;

/** FOTF Retrogen: adds newly installed mods' placed features and structures to chunks generated before them. Server only. */
@Mod("fotfretrogen")
public final class FotfRetrogen {
    public FotfRetrogen() {
        MinecraftForge.EVENT_BUS.register(new Retrogen());
    }
}
