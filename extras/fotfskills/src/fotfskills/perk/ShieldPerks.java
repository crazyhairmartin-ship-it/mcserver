package fotfskills.perk;

import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.ShieldItem;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.entity.living.LivingAttackEvent;
import net.minecraftforge.event.entity.living.LivingKnockBackEvent;
import net.minecraftforge.event.entity.living.ShieldBlockEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;

/**
 * Shield Wall (less knockback while blocking; a chance the shield takes no damage), Mana Shield (crouching with no
 * shield blocks a frontal hit from a living attacker by spending mana) and Arcane Aegis (reflects part of it as magic).
 */
public final class ShieldPerks {
    @SubscribeEvent
    public void onKnockback(LivingKnockBackEvent event) {
        if (event.getEntity() instanceof ServerPlayer player && player.m_21254_()) {
            event.setStrength((float) (event.getStrength() * (1 - Perks.get(player, "shield_wall"))));
        }
    }

    @SubscribeEvent
    public void onBlock(ShieldBlockEvent event) {
        if (event.getEntity() instanceof ServerPlayer player && Perks.roll(player, "shield_wall")) {
            event.setShieldTakesDamage(false);
        }
    }

    @SubscribeEvent
    public void onAttack(LivingAttackEvent event) {
        if (!(event.getEntity() instanceof ServerPlayer player) || !player.m_6047_()
                || player.m_21205_().m_41720_() instanceof ShieldItem || player.m_21206_().m_41720_() instanceof ShieldItem) {
            return;
        }
        double shield = Perks.get(player, "mana_shield");
        Entity attacker = event.getSource().m_7639_();
        if (shield <= 0 || !(attacker instanceof LivingEntity living) || attacker == player) {
            return;
        }
        Vec3 to = attacker.m_20182_().m_82546_(player.m_20182_()).m_82541_();
        if (to.m_82526_(player.m_20154_()) <= 0) {
            return;                                     // only hits from in front
        }
        double cost = event.getAmount() * 4 / (1 + shield);
        if (Mana.spend(player, cost)) {
            event.setCanceled(true);
            if (player.m_9236_() instanceof net.minecraft.server.level.ServerLevel level) {   // the barrier flashes where it took the hit
                double x = player.m_20185_() + to.f_82479_ * 0.8, y = player.m_20188_() - 0.4, z = player.m_20189_() + to.f_82481_ * 0.8;
                level.m_8767_(net.minecraft.core.particles.ParticleTypes.f_123808_, x, y, z, 24, 0.35, 0.5, 0.35, 0.15);
                level.m_8767_(net.minecraft.core.particles.ParticleTypes.f_123810_, x, y, z, 6, 0.3, 0.4, 0.3, 0.02);
            }
            player.m_6330_(net.minecraft.sounds.SoundEvents.f_144243_, net.minecraft.sounds.SoundSource.PLAYERS, 0.8f, 1.6f);
            double aegis = Perks.get(player, "arcane_aegis");
            if (aegis > 0) {
                living.m_6469_(player.m_269291_().m_269425_(), (float) (event.getAmount() * aegis));
            }
        }
    }
}
