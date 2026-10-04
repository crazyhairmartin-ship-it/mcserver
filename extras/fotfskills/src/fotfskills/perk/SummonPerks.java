package fotfskills.perk;

import java.util.ArrayList;
import java.util.List;
import java.util.function.Function;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.EntityJoinLevelEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;

/**
 * Artificer: summons from Ars Nouveau (wolves, steeds, vexes, undead...) and Iron's Spells (summoned wolves, skeletons,
 * vexes, polar bears...) get more health and damage. The summoner is looked up a tick after the summon joins, once its
 * mod has set the owner. Each mod's own lookup is registered only when that mod is loaded.
 */
public final class SummonPerks {
    private static final List<Function<Entity, Entity>> OWNERS = new ArrayList<>();
    private final List<LivingEntity> fresh = new ArrayList<>();

    public static void registerOwner(Function<Entity, Entity> owner) {
        OWNERS.add(owner);
    }

    @SubscribeEvent
    public void onJoin(EntityJoinLevelEvent event) {
        if (!event.getLevel().f_46443_ && !event.loadedFromDisk() && event.getEntity() instanceof LivingEntity living) {
            fresh.add(living);
        }
    }

    @SubscribeEvent
    public void onServerTick(TickEvent.ServerTickEvent event) {
        if (event.phase != TickEvent.Phase.END || fresh.isEmpty()) {
            return;
        }
        for (LivingEntity summon : fresh) {
            for (Function<Entity, Entity> lookup : OWNERS) {
                if (summon.m_6084_() && lookup.apply(summon) instanceof ServerPlayer player) {
                    double bonus = Perks.get(player, "artificer_summon");
                    if (bonus > 0) {
                        Modifiers.set(summon, Attributes.f_22276_, "artificer_health", bonus, AttributeModifier.Operation.MULTIPLY_BASE);
                        Modifiers.set(summon, Attributes.f_22281_, "artificer_damage", bonus, AttributeModifier.Operation.MULTIPLY_BASE);
                        summon.m_21153_(summon.m_21233_());
                    }
                    break;
                }
            }
        }
        fresh.clear();
    }
}
