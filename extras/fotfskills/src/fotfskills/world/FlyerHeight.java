package fotfskills.world;

import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.TamableAnimal;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.entity.living.LivingEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.registries.ForgeRegistries;

/**
 * Wild fairies (Fay's Fairies) and butterflies and moths (Butterfly Mod) stay low: more than MAX_ABOVE blocks over the
 * ground (or leaves, water) under them, they're nudged back down. Tamed fairies are free to follow their owner anywhere.
 */
public final class FlyerHeight {
    private static final double MAX_ABOVE = 5;

    @SubscribeEvent
    public void onTick(LivingEvent.LivingTickEvent event) {
        LivingEntity flyer = event.getEntity();
        if (flyer.f_19797_ % 5 != 0 || flyer.m_9236_().f_46443_) {
            return;
        }
        ResourceLocation id = ForgeRegistries.ENTITY_TYPES.getKey(flyer.m_6095_());
        if (id == null || !(id.m_135827_().equals("fays_fairies") || id.m_135827_().equals("butterflies"))) {
            return;
        }
        if (flyer instanceof TamableAnimal tame && tame.m_21824_()) {
            return;
        }
        int ground = flyer.m_9236_().m_6924_(Heightmap.Types.MOTION_BLOCKING, flyer.m_146903_(), flyer.m_146907_());
        if (flyer.m_20186_() > ground + MAX_ABOVE) {
            Vec3 v = flyer.m_20184_();
            flyer.m_20334_(v.f_82479_, Math.min(v.f_82480_, -0.15), v.f_82481_);
        }
    }
}
