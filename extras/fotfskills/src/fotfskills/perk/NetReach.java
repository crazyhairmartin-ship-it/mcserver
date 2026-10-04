package fotfskills.perk;

import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraftforge.common.ForgeMod;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.registries.ForgeRegistries;

/** Long Net: while a butterfly net (Bok's Butterflies) is in the main hand, entity reach grows by the perk. */
public final class NetReach {
    @SubscribeEvent
    public void onTick(TickEvent.PlayerTickEvent event) {
        if (event.phase != TickEvent.Phase.END || !(event.player instanceof ServerPlayer player) || player.f_19797_ % 10 != 0) {
            return;
        }
        ResourceLocation id = ForgeRegistries.ITEMS.getKey(player.m_21205_().m_41720_());
        boolean net = id != null && "butterflies".equals(id.m_135827_()) && id.m_135815_().contains("net");
        Modifiers.set(player, ForgeMod.ENTITY_REACH.get(), "long_net", net ? Perks.get(player, "long_net") : 0,
                AttributeModifier.Operation.ADDITION);
    }
}
