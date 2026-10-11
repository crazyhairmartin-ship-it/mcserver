package fotfskills.mixin;

import fotfskills.compat.OreScentOutline;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.ModifyArg;

/** Ore Scenting's ore outlines last longer: compat/OreScentOutline. */
@Mixin(targets = "com.github.alexthe668.domesticationinnovation.server.entity.TameableUtils", remap = false)
public abstract class OreScentOutlineMixin {
    @ModifyArg(method = "detectRandomOres", remap = false, at = @At(value = "INVOKE",
            target = "Lcom/github/alexthe668/domesticationinnovation/server/entity/HighlightedBlockEntity;setLifespan(I)V"))
    private static int fotfskills$longer(int ticks) {
        return OreScentOutline.lifespan(ticks);
    }
}
