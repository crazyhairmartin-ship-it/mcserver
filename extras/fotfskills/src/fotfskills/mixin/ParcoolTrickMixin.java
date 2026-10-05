package fotfskills.mixin;

import fotfskills.client.DoubleJump;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * A double jump plays ParCool's trick-jump flip: forward, or a back flip while holding back. ParCool only offers the
 * trick right after a ground jump, so this starts it once for each double jump (the trick itself still needs to be
 * unlocked, which Double Jump does).
 */
@Pseudo
@Mixin(targets = "com.alrex.parcool.common.action.impl.TrickJump", remap = false)
public abstract class ParcoolTrickMixin {
    @Inject(method = "canStart", at = @At("HEAD"), cancellable = true, remap = false, require = 0)
    private void fotfskills$flipOnDoubleJump(CallbackInfoReturnable<Boolean> cir) {
        String flip = DoubleJump.takePendingFlip();
        if (flip == null) {
            return;
        }
        try {
            Class<?> type = Class.forName("com.alrex.parcool.common.action.impl.TrickJump$Type");
            java.lang.reflect.Field property = this.getClass().getDeclaredField("propertyTrickType");
            property.setAccessible(true);
            Object holder = property.get(this);
            holder.getClass().getMethod("set", Object.class).invoke(holder, type.getMethod("valueOf", String.class).invoke(null, flip));
            cir.setReturnValue(true);
        } catch (ReflectiveOperationException | RuntimeException ignored) {
            // a ParCool update renamed something: the double jump still works, just without the flip
        }
    }
}
