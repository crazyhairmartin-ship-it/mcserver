package fotfskills.client;

import net.minecraft.client.Minecraft;
import net.minecraft.world.entity.Entity;

/**
 * Plays the Reaper's Due spin on a player: Better Combat's own two-handed spin attack animation, in place of the
 * swing it was playing (the client of every player who can see them gets the server's Spin message).
 */
public final class SpinAnimation {
    private SpinAnimation() {
    }

    public static void play(int entityId) {
        Minecraft mc = Minecraft.m_91087_();
        if (mc.f_91073_ == null || !net.minecraftforge.fml.ModList.get().isLoaded("bettercombat")) {
            return;
        }
        Entity entity = mc.f_91073_.m_6815_(entityId);
        if (entity instanceof net.bettercombat.client.animation.PlayerAttackAnimatable animatable) {
            animatable.playAttackAnimation("bettercombat:two_handed_spin", net.bettercombat.logic.AnimatedHand.TWO_HANDED, 24f, 0.35f);
        }
    }
}
