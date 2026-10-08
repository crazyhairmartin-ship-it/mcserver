package fotfskills.mixin;

import java.util.ArrayList;
import java.util.EnumSet;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import net.minecraft.client.model.WolfModel;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.core.Direction;
import net.minecraft.world.entity.animal.Wolf;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * Dale (any wolf named Dale) has floppy hound ears. In 1.20.1 a wolf's ears are two 2x2x1 boxes inside the head
 * (real_head), so they can't move; here they're swapped for two ear parts built from the same texture pixels (16,14),
 * pivoting where each ear meets the head. Normal wolves pose them exactly where the boxes were; Dale's tip outward and
 * down and hang about twice as long. All wolves share one model, so the pose is set every frame. Client only;
 * m_6973_ = setupAnim, m_171324_ = getChild, f_104200_..5_ = x/y/z and x/y/zRot, f_233553_..5_ = x/y/zScale,
 * Cube f_104336_ = minY, f_104335_/f_104338_ = minX/maxX.
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
    private void fotfskills$swapEars(ModelPart root, CallbackInfo ci) {
        try {
            ModelPart head = root.m_171324_("head").m_171324_("real_head");
            ModelPartAccessor access = (ModelPartAccessor) (Object) head;
            List<ModelPart.Cube> kept = new ArrayList<>();
            int ears = 0;
            for (ModelPart.Cube cube : access.fotfskills$cubes()) {
                boolean ear = Math.abs(cube.f_104336_ + 5) < 0.01f && Math.abs(cube.f_104338_ - cube.f_104335_ - 2) < 0.01f;
                if (ear) {
                    ears++;
                } else {
                    kept.add(cube);
                }
            }
            if (ears != 2) {
                return;                                      // not the vanilla wolf head (another mod changed it): leave it
            }
            fotfskills$rightEar = fotfskills$ear();
            fotfskills$leftEar = fotfskills$ear();
            Map<String, ModelPart> children = new HashMap<>(access.fotfskills$children());
            children.put("fotfskills_right_ear", fotfskills$rightEar);
            children.put("fotfskills_left_ear", fotfskills$leftEar);
            access.fotfskills$setCubes(kept);
            access.fotfskills$setChildren(children);
            fotfskills$pose(fotfskills$rightEar, -1, false, -FOTF_DROOP);
            fotfskills$pose(fotfskills$leftEar, 3, false, FOTF_DROOP);
        } catch (RuntimeException e) {
            fotfskills$rightEar = null;                      // never break the wolf model over ears
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
        fotfskills$pose(fotfskills$rightEar, -1, dale, -FOTF_DROOP);
        fotfskills$pose(fotfskills$leftEar, 3, dale, FOTF_DROOP);
    }

    /** One ear: the vanilla 2x2x1 box (texture 16,14 on the 64x32 wolf sheet), standing up from its pivot. */
    @Unique
    private static ModelPart fotfskills$ear() {
        ModelPart.Cube cube = new ModelPart.Cube(16, 14, -1, -2, 0, 2, 2, 1, 0, 0, 0, false, 64, 32, EnumSet.allOf(Direction.class));
        return new ModelPart(List.of(cube), Map.of());
    }

    /** Pivot at the bottom middle of where the vanilla ear box sat (x -2..0 or 2..4, y -5..-3, z 0..1). */
    @Unique
    private static void fotfskills$pose(ModelPart ear, float x, boolean floppy, float droop) {
        ear.f_104200_ = x;
        ear.f_104201_ = -3;
        ear.f_104202_ = 0;
        ear.f_104203_ = 0;
        ear.f_104204_ = 0;
        ear.f_104205_ = floppy ? droop : 0;
        ear.f_233553_ = 1;
        ear.f_233554_ = floppy ? FOTF_LENGTH : 1;
        ear.f_233555_ = 1;
    }
}
