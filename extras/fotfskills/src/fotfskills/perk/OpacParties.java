package fotfskills.perk;

import java.util.UUID;
import net.minecraft.server.MinecraftServer;
import xaero.pac.common.server.api.OpenPACServerAPI;
import xaero.pac.common.server.parties.party.api.IServerPartyAPI;

/** Open Parties and Claims party check. Loaded only if openpartiesandclaims is present. */
public final class OpacParties {
    private OpacParties() {
    }

    public static boolean same(MinecraftServer server, UUID[] ids) {
        var parties = OpenPACServerAPI.get(server).getPartyManager();
        IServerPartyAPI a = parties.getPartyByMember(ids[0]);
        IServerPartyAPI b = parties.getPartyByMember(ids[1]);
        return a != null && b != null && a.getId().equals(b.getId());
    }
}
