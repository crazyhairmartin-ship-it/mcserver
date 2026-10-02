package fotfmail.mixin;

import com.hollingsworth.arsnouveau.common.entity.goal.bookwyrm.RandomStorageVisitGoal;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * Bookwyrms (Ars Nouveau) start a "hover at a random linked chest" visit 1 time in 4 whenever they're idle, for up to
 * 10 seconds, so they mostly sit by the chests. Only let 1 in 5 of those through (about 1 in 20), leaving room for
 * BookwyrmWanderGoal. canUse = m_8036_.
 */
@Mixin(RandomStorageVisitGoal.class)
public abstract class RandomStorageVisitGoalMixin {
    @Inject(method = "m_8036_", at = @At("RETURN"), cancellable = true, remap = false)
    private void fotfmail$visitChestsLessOften(CallbackInfoReturnable<Boolean> cir) {
        if (cir.getReturnValueZ() && java.util.concurrent.ThreadLocalRandom.current().nextInt(5) != 0) {
            cir.setReturnValue(false);
        }
    }
}
