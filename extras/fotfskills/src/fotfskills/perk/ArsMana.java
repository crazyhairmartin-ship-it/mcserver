package fotfskills.perk;

import com.hollingsworth.arsnouveau.setup.registry.CapabilityRegistry;
import net.minecraft.server.level.ServerPlayer;

/** Ars Nouveau mana. Loaded only if ars_nouveau is present. */
public final class ArsMana {
    private ArsMana() {
    }

    public static void add(ServerPlayer player, double amount) {
        CapabilityRegistry.getMana(player).ifPresent(mana -> mana.addMana(amount));
    }
}
