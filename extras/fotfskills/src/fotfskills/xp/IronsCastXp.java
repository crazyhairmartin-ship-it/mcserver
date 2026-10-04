package fotfskills.xp;

import io.redspace.ironsspellbooks.api.events.SpellOnCastEvent;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.eventbus.api.SubscribeEvent;

/** Iron's Spells cast: Magic XP by mana spent. Registered only if irons_spellbooks is loaded. */
public final class IronsCastXp {
    @SubscribeEvent
    public void onCast(SpellOnCastEvent event) {
        if (event.getEntity() instanceof ServerPlayer player) {
            AmountSource.award(player, "cast_spell", event.getManaCost());
        }
    }
}
