package fotfskills.client;

import fotfskills.perk.PerkSync;
import fotfskills.perk.Perks;
import net.minecraft.client.Minecraft;
import net.minecraft.client.player.LocalPlayer;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;

/**
 * Double Jump (Agility capstone): press jump again in mid-air for one more jump per time in the air. The client moves
 * the player (movement is client-side) and tells the server, which clears the fall distance so the landing is safe.
 */
public final class DoubleJump {
    private boolean wasDown;
    private boolean used;

    @SubscribeEvent
    public void onTick(TickEvent.ClientTickEvent event) {
        Minecraft mc = Minecraft.m_91087_();
        LocalPlayer player = mc.f_91074_;
        if (event.phase != TickEvent.Phase.END || player == null) {
            return;
        }
        boolean down = mc.f_91066_.f_92089_.m_90857_();
        boolean pressed = down && !wasDown;
        wasDown = down;
        if (player.m_20096_() || player.m_20069_() || player.m_6147_()) {
            used = false;
            return;
        }
        if (!pressed || used || Perks.get(player, "double_jump") <= 0 || player.m_150110_().f_35935_
                || player.m_21255_() || player.m_20159_()) {
            return;
        }
        used = true;
        Vec3 v = player.m_20184_();
        player.m_20334_(v.f_82479_, 0.5, v.f_82481_);
        player.f_19789_ = 0;
        for (int i = 0; i < 8; i++) {
            player.m_9236_().m_7106_(ParticleTypes.f_123796_, player.m_20185_(), player.m_20186_(), player.m_20189_(),
                    (Math.random() - 0.5) * 0.2, -0.05, (Math.random() - 0.5) * 0.2);
        }
        PerkSync.sendDoubleJump();
    }
}
