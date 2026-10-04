package fotfskills.pet;

import fotfskills.perk.Perks;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.OwnableEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraftforge.event.entity.living.LivingDamageEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;

/**
 * Soul Mender: when a hit would kill a pet, its (online) owner's Soul Mender chance spares it on full health. Pets
 * that do die can still come back the next morning at their Domestication Innovation pet bed. Magic summons are
 * not pets for this.
 */
public final class SoulMender {
    private static final String[] SUMMON_INTERFACES = {"com.hollingsworth.arsnouveau.api.entity.ISummon",
            "io.redspace.ironsspellbooks.entity.mobs.IMagicSummon"};

    @SubscribeEvent(priority = EventPriority.LOWEST)
    public void onDamage(LivingDamageEvent event) {
        LivingEntity pet = event.getEntity();
        if (event.isCanceled() || pet instanceof Player || !(pet instanceof OwnableEntity owned)
                || !(owned.m_269323_() instanceof ServerPlayer owner) || event.getAmount() < pet.m_21223_()
                || isSummon(pet.getClass()) || !Perks.roll(owner, "soul_mender")) {
            return;
        }
        event.setAmount(0);
        pet.m_21153_(pet.m_21233_());
        pet.m_7292_(new MobEffectInstance(MobEffects.f_19605_, 100, 1, false, true));
        if (pet.m_9236_() instanceof ServerLevel level) {
            level.m_8767_(ParticleTypes.f_123750_, pet.m_20185_(), pet.m_20186_() + pet.m_20206_(), pet.m_20189_(), 10, 0.4, 0.3, 0.4, 0.1);
            level.m_5594_(null, pet.m_20183_(), SoundEvents.f_144243_, SoundSource.NEUTRAL, 1.0f, 1.2f);
        }
        owner.m_5661_(Component.m_237113_("§dSoul Mender §7saved " + pet.m_5446_().getString() + "!"), true);
    }

    private static boolean isSummon(Class<?> type) {
        for (Class<?> c = type; c != null; c = c.getSuperclass()) {
            for (Class<?> iface : c.getInterfaces()) {
                if (implementsSummon(iface)) {
                    return true;
                }
            }
        }
        return false;
    }

    private static boolean implementsSummon(Class<?> iface) {
        for (String name : SUMMON_INTERFACES) {
            if (iface.getName().equals(name)) {
                return true;
            }
        }
        for (Class<?> parent : iface.getInterfaces()) {
            if (implementsSummon(parent)) {
                return true;
            }
        }
        return false;
    }
}
