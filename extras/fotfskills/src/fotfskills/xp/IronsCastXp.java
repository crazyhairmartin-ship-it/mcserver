package fotfskills.xp;

import io.redspace.ironsspellbooks.api.events.SpellOnCastEvent;
import io.redspace.ironsspellbooks.api.magic.MagicData;
import java.util.HashMap;
import java.util.Map;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;

/**
 * Iron's Spells cast: Magic XP by the mana the cast really took. The event reports the full cost even for recasts,
 * scrolls, /cast and creative, so the player's mana is read at the cast and compared one tick later.
 */
public final class IronsCastXp {
    private final Map<ServerPlayer, Float> manaAtCast = new HashMap<>();

    @SubscribeEvent
    public void onCast(SpellOnCastEvent event) {
        if (event.getEntity() instanceof ServerPlayer player) {
            manaAtCast.putIfAbsent(player, MagicData.getPlayerMagicData(player).getMana());
        }
    }

    @SubscribeEvent
    public void onServerTick(TickEvent.ServerTickEvent event) {
        if (event.phase != TickEvent.Phase.END || manaAtCast.isEmpty()) {
            return;
        }
        manaAtCast.forEach((player, before) -> {
            float spent = before - MagicData.getPlayerMagicData(player).getMana();
            if (spent > 0 && !player.m_213877_()) {
                AmountSource.award(player, "cast_spell", spent);
            }
        });
        manaAtCast.clear();
    }
}
