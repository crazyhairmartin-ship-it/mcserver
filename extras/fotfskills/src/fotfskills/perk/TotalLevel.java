package fotfskills.perk;

import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.registries.ForgeRegistries;
import net.puffish.skillsmod.api.SkillsAPI;

/**
 * Overall level (all 12 skill levels added up) replaces Paragliders' heart containers and stamina vessels: every step of
 * HeartCurve gives +1 heart and +5% ParCool max stamina. Refreshed every second as transient modifiers.
 */
public final class TotalLevel {
    private static final Map<UUID, Integer> TOTALS = new ConcurrentHashMap<>();

    public static int get(UUID player) {
        return TOTALS.getOrDefault(player, 0);
    }

    @SubscribeEvent
    public void onTick(TickEvent.PlayerTickEvent event) {
        if (event.phase != TickEvent.Phase.END || !(event.player instanceof ServerPlayer player) || player.f_19797_ % 20 != 5) {
            return;
        }
        int total = SkillsAPI.streamCategories()
                .mapToInt(category -> category.getExperience().map(e -> e.getLevel(player)).orElse(0)).sum();
        TOTALS.put(player.m_20148_(), total);
        int steps = HeartCurve.steps(total);
        Modifiers.set(player, Attributes.f_22276_, "total_hearts", 2.0 * steps, AttributeModifier.Operation.ADDITION);
        Modifiers.set(player, ForgeRegistries.ATTRIBUTES.getValue(new ResourceLocation("parcool", "parcool.max_stamina")),
                "total_stamina", 0.05 * steps, AttributeModifier.Operation.MULTIPLY_BASE);
    }
}
