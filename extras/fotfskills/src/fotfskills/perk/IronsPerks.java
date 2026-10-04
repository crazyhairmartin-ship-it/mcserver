package fotfskills.perk;

import io.redspace.ironsspellbooks.api.events.SpellOnCastEvent;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;

/** Mana Saver / Archmage for Iron's Spells: the cast costs no mana (and so earns no Magic XP: XP follows the mana really spent). */
public final class IronsPerks {
    @SubscribeEvent(priority = EventPriority.LOWEST)
    public void onCast(SpellOnCastEvent event) {
        if (event.getEntity() instanceof ServerPlayer caster) {
            CombatState.of(caster).lastCast = CombatState.now(caster);      // Spellbound Steel
        }
        if (event.getEntity() instanceof ServerPlayer player && Perks.roll(player, "free_spell")) {
            event.setManaCost(0);
        }
    }
}
