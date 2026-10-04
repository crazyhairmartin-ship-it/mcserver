package fotfskills.perk;

import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.registries.ForgeRegistries;
import net.puffish.skillsmod.api.SkillsAPI;

/**
 * Overall level (all 12 skill levels added up) replaces Paragliders' heart containers and stamina vessels: every step of
 * HeartCurve gives +1 heart and +5% ParCool max stamina. The hearts are a permanent (saved) modifier, so health is kept
 * across relogs and restarts; on respawn they are applied at once and the player is healed to the new maximum.
 */
public final class TotalLevel {
    private static final Map<UUID, Integer> TOTALS = new ConcurrentHashMap<>();
    private static final UUID HEARTS = Modifiers.uuid("total_hearts");

    public static int get(UUID player) {
        return TOTALS.getOrDefault(player, 0);
    }

    @SubscribeEvent
    public void onTick(TickEvent.PlayerTickEvent event) {
        if (event.phase == TickEvent.Phase.END && event.player instanceof ServerPlayer player && player.f_19797_ % 20 == 5) {
            apply(player);
        }
    }

    @SubscribeEvent
    public void onRespawn(PlayerEvent.PlayerRespawnEvent event) {
        if (event.getEntity() instanceof ServerPlayer player && !event.isEndConquered()) {
            apply(player);
            player.m_21153_(player.m_21233_());
        }
    }

    @SubscribeEvent
    public void onLogout(PlayerEvent.PlayerLoggedOutEvent event) {
        TOTALS.remove(event.getEntity().m_20148_());
    }

    private static void apply(ServerPlayer player) {
        int total = SkillsAPI.streamCategories()
                .mapToInt(category -> category.getExperience().map(e -> e.getLevel(player)).orElse(0)).sum();
        TOTALS.put(player.m_20148_(), total);
        int steps = HeartCurve.steps(total);
        setHearts(player, 2.0 * steps);
        Modifiers.set(player, ForgeRegistries.ATTRIBUTES.getValue(new ResourceLocation("parcool", "parcool.max_stamina")),
                "total_stamina", 0.05 * steps, AttributeModifier.Operation.MULTIPLY_BASE);
    }

    private static void setHearts(ServerPlayer player, double value) {
        AttributeInstance health = player.m_21051_(Attributes.f_22276_);
        if (health == null) {
            return;
        }
        AttributeModifier old = health.m_22111_(HEARTS);
        if (old != null && old.m_22218_() == value) {
            return;
        }
        if (old != null) {
            health.m_22120_(HEARTS);
        }
        if (value > 0) {
            health.m_22125_(new AttributeModifier(HEARTS, "fotfskills total level", value, AttributeModifier.Operation.ADDITION));
        }
        if (player.m_21223_() > player.m_21233_()) {
            player.m_21153_(player.m_21233_());
        }
    }
}
