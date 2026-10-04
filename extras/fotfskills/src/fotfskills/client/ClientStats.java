package fotfskills.client;

import net.minecraft.world.entity.player.Player;

/** Stamina (ParCool) and mana (Iron's Spells) for the character screen; each is only called when its mod is loaded. */
public final class ClientStats {
    private ClientStats() {
    }

    public static double[] stamina(Player player) {
        com.alrex.parcool.common.Parkourability parkour = com.alrex.parcool.common.Parkourability.get(player);
        if (parkour == null || parkour.getStamina() == null) {
            return new double[] {0, 0};
        }
        return new double[] {parkour.getStamina().value(), parkour.getStamina().max()};
    }

    public static double[] mana(Player player) {
        double max = player.m_21133_(io.redspace.ironsspellbooks.api.registry.AttributeRegistry.MAX_MANA.get());
        return new double[] {io.redspace.ironsspellbooks.player.ClientMagicData.getPlayerMana(), max};
    }
}
