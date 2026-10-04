package fotfskills.perk;

import io.redspace.ironsspellbooks.api.events.SpellOnCastEvent;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;

/**
 * Iron's Spells perks: Druid's Grove (cheaper in forests), Mana Saver / Archmage (free casts, which then earn no Magic
 * XP since XP follows the mana really spent), plus casting marks for Spellbound Steel and Nature's Mend.
 */
public final class IronsPerks {
    @SubscribeEvent(priority = EventPriority.LOWEST)
    public void onCast(SpellOnCastEvent event) {
        if (!(event.getEntity() instanceof ServerPlayer caster)) {
            return;
        }
        CombatState.of(caster).lastCast = CombatState.now(caster);      // Spellbound Steel
        if (event.getSpellId().contains("heal")) {                       // Nature's Mend
            PetPerks.healPets(caster, 2 * event.getSpellLevel() * Perks.get(caster, "natures_mend"));
        }
        double grove = Perks.get(caster, "druids_grove");
        if (grove > 0 && Biomes.inForest(caster)) {
            event.setManaCost((int) Math.round(event.getManaCost() * (1 - grove)));
        }
        if (Perks.roll(caster, "free_spell")) {
            event.setManaCost(0);
        }
    }
}
