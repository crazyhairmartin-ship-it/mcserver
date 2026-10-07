package fotfretrogen;

import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import xaero.pac.common.server.api.OpenPACServerAPI;
import xaero.pac.common.server.claims.api.IServerClaimsManagerAPI;

/** Open Parties and Claims check for Retrogen. Loaded only if openpartiesandclaims is present. */
final class RetrogenClaims {
    private RetrogenClaims() {
    }

    /** Whether any chunk within {@code radius} chunks of (x, z) is claimed. */
    static boolean near(ServerLevel level, int x, int z, int radius) {
        IServerClaimsManagerAPI claims = OpenPACServerAPI.get(level.m_7654_()).getServerClaimsManager();
        ResourceLocation dimension = level.m_46472_().m_135782_();
        for (int dx = -radius; dx <= radius; dx++) {
            for (int dz = -radius; dz <= radius; dz++) {
                if (claims.get(dimension, x + dx, z + dz) != null) {
                    return true;
                }
            }
        }
        return false;
    }
}
