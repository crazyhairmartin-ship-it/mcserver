package fotfskills.perk;

import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.AgeableMob;
import net.minecraft.world.entity.ai.attributes.Attribute;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.animal.horse.AbstractHorse;
import net.minecraftforge.event.entity.living.BabyEntitySpawnEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;

/** Breeder (twins, faster growth), Selective Breeding and Prized Stock (foal stats) on player-caused breeding. */
public final class BreedingPerks {
    private static final Attribute[] HORSE_STATS = {Attributes.f_22276_, Attributes.f_22279_, Attributes.f_22288_};
    private static final double[] VANILLA_MAX = {30, 0.3375, 1.0};

    @SubscribeEvent(priority = EventPriority.LOW)
    public void onBaby(BabyEntitySpawnEvent event) {
        if (event.isCanceled() || !(event.getCausedByPlayer() instanceof ServerPlayer player) || event.getChild() == null
                || !(event.getParentA() instanceof AgeableMob a) || !(event.getParentB() instanceof AgeableMob b)) {
            return;
        }
        AgeableMob child = event.getChild();
        shape(player, child, a, b);
        if (Perks.roll(player, "twins") && a.m_9236_() instanceof ServerLevel level) {
            AgeableMob twin = a.m_142606_(level, b);
            if (twin != null) {
                twin.m_6863_(true);
                twin.m_7678_(a.m_20185_(), a.m_20186_(), a.m_20189_(), 0, 0);
                shape(player, twin, a, b);
                level.m_7967_(twin);
            }
        }
    }

    /** Faster growth for every baby; better-parent stats (and bonuses) for foals. */
    private static void shape(ServerPlayer player, AgeableMob child, AgeableMob a, AgeableMob b) {
        double growth = Perks.get(player, "growth");
        if (growth > 0) {
            child.m_146762_((int) (-24000 * (1 - growth)));
        }
        if (Perks.get(player, "breed_bonus") > 0 && child instanceof AbstractHorse && a instanceof AbstractHorse && b instanceof AbstractHorse) {
            double prized = Perks.get(player, "prized_stock");
            for (int i = 0; i < HORSE_STATS.length; i++) {
                AttributeInstance ci = child.m_21051_(HORSE_STATS[i]);
                AttributeInstance ai = a.m_21051_(HORSE_STATS[i]);
                AttributeInstance bi = b.m_21051_(HORSE_STATS[i]);
                if (ci != null && ai != null && bi != null) {
                    ci.m_22100_(Breeding.stat(ai.m_22115_(), bi.m_22115_(), Perks.roll(player, "breed_bonus"), VANILLA_MAX[i], prized));
                }
            }
            child.m_21153_(child.m_21233_());
        }
    }
}
