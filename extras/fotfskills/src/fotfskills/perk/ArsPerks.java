package fotfskills.perk;

import com.hollingsworth.arsnouveau.api.event.ManaRegenCalcEvent;
import com.hollingsworth.arsnouveau.api.event.SpellCostCalcEvent;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.eventbus.api.SubscribeEvent;

/** Ars Nouveau perks: Druid's Grove (cheaper in forests), Mana Saver / Archmage (free spells), Wellspring (faster regen out of combat). */
public final class ArsPerks {
    @SubscribeEvent
    public void onCost(SpellCostCalcEvent event) {
        if (!(event.context.getUnwrappedCaster() instanceof ServerPlayer player)) {
            return;
        }
        double grove = Perks.get(player, "druids_grove");
        if (grove > 0 && Biomes.inForest(player)) {
            event.currentCost = (int) Math.round(event.currentCost * (1 - grove));
        }
        if (Perks.roll(player, "free_spell")) {
            event.currentCost = 0;
        }
    }

    @SubscribeEvent
    public void onRegen(ManaRegenCalcEvent event) {
        if (fotfskills.mana.ManaMerge.active()) {
            return;                                         // shared mana: Iron's Wellspring covers the pool
        }
        if (event.getEntity() instanceof ServerPlayer player && CombatState.now(player) - CombatState.of(player).lastCombat > 200) {
            event.setRegen(event.getRegen() * (1 + Perks.get(player, "wellspring")));
        }
    }
}
