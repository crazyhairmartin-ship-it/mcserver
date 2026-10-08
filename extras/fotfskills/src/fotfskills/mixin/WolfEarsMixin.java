package fotfskills.mixin;

import net.minecraft.client.model.WolfModel;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.world.entity.animal.Wolf;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * Dale (any wolf named Dale) has floppy hound ears: the ears tip outward and down beside the head and hang about twice
 * as long, using his own ear pixels. All wolves share one model, so every other wolf gets the normal ears back each
 * frame. Client only; m_6973_ = setupAnim, m_171324_ = getChild, m_233569_ = resetPose, f_104205_ = zRot,
 * f_233553_..5_ = x/y/zScale.
 */
@Mixin(value = WolfModel.class, remap = false)
public abstract class WolfEarsMixin {
    @Unique
    private static final float FOTF_DROOP = 2.6f;          // about 150 degrees: tipped over, hanging outward
    @Unique
    private static final float FOTF_LENGTH = 2.2f;

    @Unique
    private ModelPart fotfskills$rightEar;
    @Unique
    private ModelPart fotfskills$leftEar;

    @Inject(method = "<init>", at = @At("RETURN"), remap = false)
    private void fotfskills$findEars(ModelPart root, CallbackInfo ci) {
        try {
            ModelPart head = root.m_171324_("head").m_171324_("real_head");
            fotfskills$rightEar = head.m_171324_("right_ear");
            fotfskills$leftEar = head.m_171324_("left_ear");
        } catch (java.util.NoSuchElementException e) {
            fotfskills$rightEar = null;                     // 1.20.1: the ears are boxes inside real_head, not parts
            fotfskills$leftEar = null;
        }
    }

    @Inject(method = "m_6973_(Lnet/minecraft/world/entity/animal/Wolf;FFFFF)V", at = @At("TAIL"), remap = false)
    private void fotfskills$floppyEars(Wolf wolf, float limbSwing, float limbAmount, float age, float yaw, float pitch,
                                       CallbackInfo ci) {
        if (fotfskills$rightEar == null || fotfskills$leftEar == null) {
            return;
        }
        boolean dale = wolf.m_8077_() && wolf.m_7770_() != null && wolf.m_7770_().getString().trim().equalsIgnoreCase("dale");
        fotfskills$ear(fotfskills$rightEar, dale, -FOTF_DROOP);
        fotfskills$ear(fotfskills$leftEar, dale, FOTF_DROOP);
    }

    @Unique
    private static void fotfskills$ear(ModelPart ear, boolean floppy, float droop) {
        ear.m_233569_();
        ear.f_233553_ = 1;
        ear.f_233554_ = floppy ? FOTF_LENGTH : 1;
        ear.f_233555_ = 1;
        if (floppy) {
            ear.f_104205_ = droop;
        }
    }
}
