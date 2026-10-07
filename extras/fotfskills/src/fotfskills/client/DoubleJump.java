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
 * With an Artifacts Cloud in a Bottle worn too, the bottle's jump goes first and this one comes after: a triple jump.
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
        if (cloudJumpReady(player)) {
            return;                                // the Cloud in a Bottle takes this press; the skill's jump is the next one
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

    private static java.lang.reflect.Field cloudReady;
    private static java.lang.reflect.Field cloudItem;
    private static boolean cloudLookedUp;

    /** True while an equipped Artifacts Cloud in a Bottle still has its air jump (read from Artifacts by reflection). */
    private static boolean cloudJumpReady(LocalPlayer player) {
        if (!net.minecraftforge.fml.ModList.get().isLoaded("artifacts")) {
            return false;
        }
        try {
            if (!cloudLookedUp) {
                cloudLookedUp = true;
                cloudReady = Class.forName("artifacts.client.CloudInABottleInputHandler").getDeclaredField("canDoubleJump");
                cloudReady.setAccessible(true);
                cloudItem = Class.forName("artifacts.registry.ModItems").getField("CLOUD_IN_A_BOTTLE");
            }
            if (cloudReady == null || !cloudReady.getBoolean(null)) {
                return false;
            }
            Object item = ((java.util.function.Supplier<?>) cloudItem.get(null)).get();
            return (Boolean) item.getClass().getMethod("isEquippedBy", net.minecraft.world.entity.LivingEntity.class).invoke(item, player);
        } catch (ReflectiveOperationException | RuntimeException e) {
            cloudReady = null;                     // Artifacts changed: just jump as if there's no bottle
            return false;
        }
    }

    public static String takePendingFlip() {
        String flip = pendingFlip;
        pendingFlip = null;
        return flip != null && System.currentTimeMillis() <= pendingUntil ? flip : null;
    }
}
