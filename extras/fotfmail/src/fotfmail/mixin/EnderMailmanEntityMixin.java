package fotfmail.mixin;

import com.chaosthedude.endermail.entity.EnderMailmanEntity;
import fotfmail.CarrierGoal;
import net.minecraft.core.NonNullList;
import net.minecraft.world.item.ItemStack;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * Ender Mail's carrier, for fotfmail letters (persistent data flag "fotfmail_letter"):
 * - CarrierGoal (priority 0, registerGoals = m_8099_) walks the letter between the two mailboxes
 * - no random enderman teleports (in daylight or when hurt), which would break the walk
 * - getPackageStack hands over the letter itself rather than wrapping it in a package (only reached if Ender Mail's
 *   own delivery somehow runs; its goals are off for letter carriers, see EnderMailmanGoalsMixin)
 */
@Mixin(EnderMailmanEntity.class)
public abstract class EnderMailmanEntityMixin {
    @Inject(method = "m_8099_", at = @At("TAIL"), remap = false)
    private void fotfmail$addCarrierGoal(CallbackInfo ci) {
        EnderMailmanEntity self = (EnderMailmanEntity) (Object) this;
        ((MobAccessor) self).fotfmail$goalSelector().m_25352_(0, new CarrierGoal(self));
    }

    @Inject(method = "teleportRandomly", at = @At("HEAD"), cancellable = true, remap = false)
    private void fotfmail$stayPut(CallbackInfoReturnable<Boolean> cir) {
        if (CarrierGoal.isLetterCarrier((EnderMailmanEntity) (Object) this)) {
            cir.setReturnValue(false);
        }
    }

    @Inject(method = "getPackageStack", at = @At("HEAD"), cancellable = true, remap = false)
    private void fotfmail$deliverLetterItself(CallbackInfoReturnable<ItemStack> cir) {
        EnderMailmanEntity self = (EnderMailmanEntity) (Object) this;
        NonNullList<ItemStack> contents = self.getContents();
        if (CarrierGoal.isLetterCarrier(self) && !contents.isEmpty() && !contents.get(0).m_41619_()) {
            cir.setReturnValue(contents.get(0).m_41777_());
        }
    }
}
