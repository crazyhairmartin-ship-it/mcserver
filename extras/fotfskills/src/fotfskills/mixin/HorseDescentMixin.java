package fotfskills.mixin;

import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** Flying horses (Wings Horns & Hooves) go down half as fast when the rider holds the descend key (-0.2 -> -0.1 per tick). */
@Pseudo
@Mixin(targets = "com.hackshop.ultimate_unicorn.entity.horses.MagicalHorse", remap = false)
public abstract class HorseDescentMixin {
    @Inject(method = "getFlightDescendAmount", at = @At("RETURN"), cancellable = true, remap = false, require = 0)
    private void fotfskills$gentlerDescent(CallbackInfoReturnable<Double> cir) {
        cir.setReturnValue(cir.getReturnValue() * 0.5);
    }
}
