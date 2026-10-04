package fotfskills.perk;

import io.redspace.ironsspellbooks.api.events.SpellOnCastEvent;
import io.redspace.ironsspellbooks.api.spells.CastSource;
import io.redspace.ironsspellbooks.item.Scroll;
import java.util.ArrayList;
import java.util.List;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.items.ItemHandlerHelper;

/**
 * Iron's Spells perks: Druid's Grove (cheaper in forests), Mana Saver / Archmage (free casts, which then earn no Magic
 * XP since XP follows the mana really spent), Scroll Saver (a used scroll may come back), plus casting marks for
 * Spellbound Steel and Nature's Mend.
 */
public final class IronsPerks {
    private record ScrollUse(ServerPlayer player, InteractionHand hand, ItemStack scroll, int before) {
    }

    private final List<ScrollUse> scrolls = new ArrayList<>();

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
        if (event.getCastSource() == CastSource.SCROLL && Perks.roll(caster, "scroll_saver")) {
            for (InteractionHand hand : InteractionHand.values()) {
                ItemStack held = caster.m_21120_(hand);
                if (held.m_41720_() instanceof Scroll) {
                    ItemStack copy = held.m_41777_();
                    copy.m_41764_(1);
                    scrolls.add(new ScrollUse(caster, hand, copy, held.m_41613_()));
                    break;
                }
            }
        }
    }

    /** Scroll Saver: only a scroll that was really used up comes back (checked one tick after the cast). */
    @SubscribeEvent
    public void onServerTick(TickEvent.ServerTickEvent event) {
        if (event.phase != TickEvent.Phase.END || scrolls.isEmpty()) {
            return;
        }
        for (ScrollUse use : scrolls) {
            ItemStack now = use.player.m_21120_(use.hand);
            int count = ItemStack.m_150942_(now, use.scroll) ? now.m_41613_() : 0;
            if (count == use.before - 1) {
                ItemHandlerHelper.giveItemToPlayer(use.player, use.scroll.m_41777_());
            }
        }
        scrolls.clear();
    }
}
