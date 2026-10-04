package fotfskills.mana;

import com.hollingsworth.arsnouveau.setup.config.ServerConfig;
import fotfskills.perk.Modifiers;
import io.redspace.ironsspellbooks.api.registry.AttributeRegistry;
import io.redspace.ironsspellbooks.config.ServerConfigs;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;

/**
 * Every second: Ars's max mana and regen above its own base (glyphs, book tier, Mana Boost / Mana Regen enchantments,
 * Ars gear) become Iron's max mana and mana regen bonuses on the shared pool. Loaded only when both mods are present.
 */
public final class ManaMergeTicker {
    @SubscribeEvent
    public void onTick(TickEvent.PlayerTickEvent event) {
        if (event.phase != TickEvent.Phase.END || !(event.player instanceof ServerPlayer player) || player.f_19797_ % 20 != 15) {
            return;
        }
        Integer arsMax = ManaMerge.arsMax(player.m_20148_());
        int maxBonus = arsMax == null ? 0 : ManaMath.maxBonus(arsMax, ServerConfig.INIT_MAX_MANA.get());
        Modifiers.set(player, AttributeRegistry.MAX_MANA.get(), "ars_max_bonus", maxBonus, AttributeModifier.Operation.ADDITION);
        Double arsRegen = ManaMerge.arsRegen(player.m_20148_());
        double regenBonus = arsRegen == null ? 0 : ManaMath.regenBonus(arsRegen, ServerConfig.INIT_MANA_REGEN.get(),
                player.m_21133_(AttributeRegistry.MAX_MANA.get()), ServerConfigs.MANA_REGEN_MULTIPLIER.get());
        Modifiers.set(player, AttributeRegistry.MANA_REGEN.get(), "ars_regen_bonus", Math.round(regenBonus * 1000) / 1000.0,
                AttributeModifier.Operation.ADDITION);
    }

    @SubscribeEvent
    public void onLogout(PlayerEvent.PlayerLoggedOutEvent event) {
        ManaMerge.forget(event.getEntity().m_20148_());
    }
}
