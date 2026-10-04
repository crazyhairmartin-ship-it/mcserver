package fotfskills.mixin;

import fotfskills.perk.Perks;
import net.minecraft.client.Minecraft;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.ModifyArg;

/** Longer dodges: ParCool scales the dodge by your top speed; everyone gets 60% more (faster and further), Roll Master +10% per rank. */
@Pseudo
@Mixin(targets = "com.alrex.parcool.common.action.impl.Dodge", remap = false)
public abstract class ParcoolDodgeMixin {
    @ModifyArg(method = "onStartInLocalClient", remap = false, require = 0,
            at = @At(value = "INVOKE", target = "Lnet/minecraft/world/phys/Vec3;m_82490_(D)Lnet/minecraft/world/phys/Vec3;", ordinal = 0, remap = false))
    private double fotfskills$furtherDodge(double speed) {
        Minecraft mc = Minecraft.m_91087_();
        double bonus = mc.f_91074_ == null ? 0 : Perks.get(mc.f_91074_, "dodge_distance");
        return speed * (1.6 + bonus);
    }
}
