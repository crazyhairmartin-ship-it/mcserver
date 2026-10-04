package fotfskills.perk;

import com.hollingsworth.arsnouveau.api.event.SpellCostCalcEvent;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.eventbus.api.SubscribeEvent;

/** Mana Saver / Archmage for Ars Nouveau: the spell costs no mana. */
public final class ArsPerks {
    @SubscribeEvent
    public void onCost(SpellCostCalcEvent event) {
        if (event.context.getUnwrappedCaster() instanceof ServerPlayer player && Perks.roll(player, "free_spell")) {
            event.currentCost = 0;
        }
    }
}
