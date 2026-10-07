package fotfskills.client;

import dev.kosmx.playerAnim.api.layered.IAnimation;
import dev.kosmx.playerAnim.api.layered.KeyframeAnimationPlayer;
import dev.kosmx.playerAnim.api.layered.ModifierLayer;
import dev.kosmx.playerAnim.core.data.KeyframeAnimation;
import dev.kosmx.playerAnim.minecraftApi.PlayerAnimationAccess;
import dev.kosmx.playerAnim.minecraftApi.PlayerAnimationRegistry;
import java.util.Map;
import java.util.WeakHashMap;
import net.minecraft.client.Minecraft;
import net.minecraft.client.player.AbstractClientPlayer;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.Entity;

/**
 * Plays the Reaper's Due spin (assets/fotfskills/player_animation/reaper_spin.json) on a player, through playerAnimator
 * (the animation library Better Combat uses). Each player gets one extra animation layer above Better Combat's.
 */
public final class SpinAnimation {
    private static final ResourceLocation SPIN = new ResourceLocation("fotfskills", "reaper_spin");
    private static final Map<AbstractClientPlayer, ModifierLayer<IAnimation>> LAYERS = new WeakHashMap<>();

    private SpinAnimation() {
    }

    public static void play(int entityId) {
        Minecraft mc = Minecraft.m_91087_();
        if (mc.f_91073_ == null || !net.minecraftforge.fml.ModList.get().isLoaded("playeranimator")) {
            return;
        }
        Entity entity = mc.f_91073_.m_6815_(entityId);
        KeyframeAnimation spin = PlayerAnimationRegistry.getAnimation(SPIN);
        if (!(entity instanceof AbstractClientPlayer player) || spin == null) {
            return;
        }
        ModifierLayer<IAnimation> layer = LAYERS.computeIfAbsent(player, p -> {
            ModifierLayer<IAnimation> created = new ModifierLayer<>();
            PlayerAnimationAccess.getPlayerAnimLayer(p).addAnimLayer(3000, created);
            return created;
        });
        layer.setAnimation(new KeyframeAnimationPlayer(spin));
    }
}
