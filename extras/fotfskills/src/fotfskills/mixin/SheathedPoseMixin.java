package fotfskills.mixin;

import dev.kosmx.playerAnim.core.data.KeyframeAnimation;
import fotfskills.client.SheathedPose;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.ModifyVariable;

/**
 * Better Combat's pose layer sets no stance while Weapon Master has that hand's weapon put away (client/SheathedPose).
 * setPose skips repeats, so asking for "no stance" every tick is steady, not a flicker.
 */
@Mixin(targets = "net.bettercombat.client.animation.PoseSubStack", remap = false)
public abstract class SheathedPoseMixin {
    @Shadow
    @Final
    private boolean isMainHand;

    @ModifyVariable(method = "setPose", remap = false, at = @At("HEAD"), argsOnly = true)
    private KeyframeAnimation fotfskills$sheathed(KeyframeAnimation animation) {
        return animation != null && SheathedPose.sheathed(this, isMainHand) ? null : animation;
    }
}
