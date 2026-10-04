package fotfskills.perk;

import io.redspace.ironsspellbooks.api.magic.MagicData;
import io.redspace.ironsspellbooks.api.registry.AttributeRegistry;
import net.minecraft.server.level.ServerPlayer;

/** Iron's Spells mana, clamped to the player's max mana. Loaded only if irons_spellbooks is present. */
public final class IronsMana {
    private IronsMana() {
    }

    public static void add(ServerPlayer player, double amount) {
        MagicData data = MagicData.getPlayerMagicData(player);
        double max = player.m_21133_(AttributeRegistry.MAX_MANA.get());
        data.setMana((float) Math.min(max, data.getMana() + amount));
    }

    public static boolean spend(ServerPlayer player, double amount) {
        MagicData data = MagicData.getPlayerMagicData(player);
        if (data.getMana() < amount) {
            return false;
        }
        data.setMana((float) (data.getMana() - amount));
        return true;
    }

    public static double get(ServerPlayer player) {
        return MagicData.getPlayerMagicData(player).getMana();
    }

    public static double max(ServerPlayer player) {
        return player.m_21133_(AttributeRegistry.MAX_MANA.get());
    }

    /** Sets Iron's mana within 0..max and returns the new value (shared mana: Ars's set mana lands here). */
    public static double set(ServerPlayer player, double mana) {
        float value = (float) Math.max(0, Math.min(max(player), mana));
        MagicData.getPlayerMagicData(player).setMana(value);
        return value;
    }
}
