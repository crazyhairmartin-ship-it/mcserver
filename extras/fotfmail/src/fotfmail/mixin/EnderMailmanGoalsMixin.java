package fotfmail.mixin;

import com.chaosthedude.endermail.entity.EnderMailmanEntity;
import fotfmail.CarrierGoal;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * Ender Mail's own carrier goals (take package, deliver, despawn) never start for fotfmail letter carriers; CarrierGoal
 * handles those. In particular the take-package goal removes the block at the carrier's start, which for a letter
 * would be the sender's mailbox. canUse = m_8036_.
 */
@Mixin(targets = {
        "com.chaosthedude.endermail.entity.EnderMailmanEntity$TakePackageGoal",
        "com.chaosthedude.endermail.entity.EnderMailmanEntity$DeliverGoal",
        "com.chaosthedude.endermail.entity.EnderMailmanEntity$DieGoal"})
public abstract class EnderMailmanGoalsMixin {
    @Shadow(remap = false)
    @Final
    private EnderMailmanEntity enderMailman;

    @Inject(method = "m_8036_", at = @At("HEAD"), cancellable = true, remap = false)
    private void fotfmail$notForLetters(CallbackInfoReturnable<Boolean> cir) {
        if (CarrierGoal.isLetterCarrier(enderMailman)) {
            cir.setReturnValue(false);
        }
    }
}
