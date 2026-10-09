package fotfskills.mixin;

import io.redspace.ironsspellbooks.block.BloodCauldronBlock;
import net.minecraft.world.phys.AABB;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Redirect;

/** Iron's blood cauldron overlap test also counts a mob standing on the rim (see compat/BloodCauldronMobs). */
@Mixin(value = BloodCauldronBlock.class, remap = false)
public abstract class BloodCauldronReachMixin {
    @Redirect(method = "attemptCookEntity", remap = false, at = @At(value = "INVOKE",
            target = "Lnet/minecraft/world/phys/AABB;m_82381_(Lnet/minecraft/world/phys/AABB;)Z"))
    private static boolean fotfskills$rim(AABB mob, AABB cauldron) {
        return mob.m_82381_(cauldron) || mob.m_82386_(0, -0.2, 0).m_82381_(cauldron);
    }
}
