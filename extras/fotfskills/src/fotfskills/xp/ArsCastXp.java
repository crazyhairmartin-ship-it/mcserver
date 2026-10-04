package fotfskills.xp;

import com.hollingsworth.arsnouveau.api.event.SpellCastEvent;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.eventbus.api.SubscribeEvent;

/** Ars Nouveau cast: Magic XP by the spell's mana cost. Registered only if ars_nouveau is loaded. */
public final class ArsCastXp {
    @SubscribeEvent
    public void onCast(SpellCastEvent event) {
        if (event.getEntity() instanceof ServerPlayer player && !event.isCanceled()) {
            AmountSource.award(player, "cast_spell", event.spell.getCost());
        }
    }
}
