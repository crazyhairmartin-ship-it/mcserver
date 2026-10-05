package fotfskills.client;

import fotfskills.perk.PerkSync;
import fotfskills.perk.Perks;
import net.minecraft.client.Minecraft;
import net.minecraft.client.player.LocalPlayer;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.client.event.InputEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;

/**
 * Double Jump (Agility capstone): press jump again in mid-air for one more jump per time in the air. Reacts to the key
 * press itself (a once-per-tick check missed quick taps). The client moves the player (movement is client-side) and
 * tells the server, which clears the fall distance so the landing is safe. It also plays ParCool's flip (ParcoolTrickMixin).
 */
public final class DoubleJump {
    /** The flip a double jump asked ParCool to play ("FORWARD" or "BACK"), taken by ParcoolTrickMixin within a few ticks. */
    private static volatile String pendingFlip;
    private static volatile long pendingUntil;
    private boolean used;
    private boolean leftGround;

    @SubscribeEvent
    public void onTick(TickEvent.ClientTickEvent event) {
        LocalPlayer player = Minecraft.m_91087_().f_91074_;
        if (event.phase != TickEvent.Phase.END || player == null) {
            return;
        }
        if (player.m_20096_() || player.m_20069_() || player.m_6147_()) {
            used = false;
            leftGround = false;
        } else {
            leftGround = true;                     // a press only counts once the first jump is off the ground
        }
    }

    @SubscribeEvent
    public void onKey(InputEvent.Key event) {
        Minecraft mc = Minecraft.m_91087_();
        LocalPlayer player = mc.f_91074_;
        if (event.getAction() != 1 /* GLFW_PRESS */ || player == null || mc.f_91080_ != null
                || !mc.f_91066_.f_92089_.m_90832_(event.getKey(), event.getScanCode())) {
            return;
        }
        if (!leftGround || used || player.m_20096_() || player.m_20069_() || player.m_6147_()
                || Perks.get(player, "double_jump") <= 0 || player.m_150110_().f_35935_ || player.m_21255_() || player.m_20159_()) {
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
        pendingFlip = mc.f_91066_.f_92087_.m_90857_() ? "BACK" : "FORWARD";
        pendingUntil = System.currentTimeMillis() + 300;
    }

    public static String takePendingFlip() {
        String flip = pendingFlip;
        pendingFlip = null;
        return flip != null && System.currentTimeMillis() <= pendingUntil ? flip : null;
    }
}
