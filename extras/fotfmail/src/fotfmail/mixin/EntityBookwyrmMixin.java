package fotfmail.mixin;

import com.hollingsworth.arsnouveau.common.entity.EntityBookwyrm;
import fotfmail.BookwyrmWanderGoal;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * Gives Ars Nouveau's Bookwyrms an idle wander around their lectern (registerGoals = m_8099_). Priority 4, the same
 * as their random chest visits (so they take turns), below chest transfers (2) and above look-around goals (7, 8).
 */
@Mixin(EntityBookwyrm.class)
public abstract class EntityBookwyrmMixin {
    @Inject(method = "m_8099_", at = @At("TAIL"), remap = false)
    private void fotfmail$addWander(CallbackInfo ci) {
        EntityBookwyrm self = (EntityBookwyrm) (Object) this;
        ((MobAccessor) self).fotfmail$goalSelector().m_25352_(4, new BookwyrmWanderGoal(self));
    }
}
