package fotfskills.world;

import java.util.Set;
import net.minecraft.tags.FluidTags;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.entity.living.LivingEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;

/**
 * Pegasi and nightmares (Wings Horns & Hooves) float in deep water like vanilla horses instead of sinking and drowning,
 * ridden or not. Runs on both sides: a ridden horse is moved by its rider's client.
 */
public final class HorseSwim {
    private static final Set<String> FLOATERS = Set.of("com.hackshop.ultimate_unicorn.entity.horses.Pegasus",
            "com.hackshop.ultimate_unicorn.entity.horses.Nightmare");

    @SubscribeEvent
    public void onTick(LivingEvent.LivingTickEvent event) {
        LivingEntity horse = event.getEntity();
        if (!horse.m_20069_() || !FLOATERS.contains(horse.getClass().getName())) {
            return;
        }
        if (horse.m_204036_(FluidTags.f_13131_) > horse.m_20206_() * 0.45) {   // deeper than about half its height
            Vec3 v = horse.m_20184_();
            horse.m_20334_(v.f_82479_, Math.min(0.12, Math.max(v.f_82480_, 0) + 0.06), v.f_82481_);
        }
    }
}
