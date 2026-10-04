package fotfskills.perk;

import java.util.UUID;
import java.util.function.BiPredicate;
import net.minecraft.server.MinecraftServer;

/** Whether two players share a party (Open Parties and Claims bridge, registered when OPAC is loaded). */
public final class Parties {
    private static BiPredicate<MinecraftServer, UUID[]> bridge = (server, ids) -> false;

    private Parties() {
    }

    public static void register(BiPredicate<MinecraftServer, UUID[]> partyCheck) {
        bridge = partyCheck;
    }

    public static boolean same(MinecraftServer server, UUID a, UUID b) {
        return bridge.test(server, new UUID[] {a, b});
    }
}
