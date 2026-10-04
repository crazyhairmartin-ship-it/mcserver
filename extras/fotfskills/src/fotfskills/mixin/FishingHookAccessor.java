package fotfskills.mixin;

import net.minecraft.world.entity.projectile.FishingHook;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Accessor;

/** timeUntilLured (f_37090_) for mods' own bobbers that extend FishingHook (Aquaculture). */
@Mixin(value = FishingHook.class, remap = false)
public interface FishingHookAccessor {
    @Accessor(value = "f_37090_", remap = false)
    int fotfskills$getTimeUntilLured();

    @Accessor(value = "f_37090_", remap = false)
    void fotfskills$setTimeUntilLured(int ticks);
}
