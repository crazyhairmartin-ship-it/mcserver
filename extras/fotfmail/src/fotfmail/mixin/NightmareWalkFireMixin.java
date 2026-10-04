package fotfmail.mixin;

import com.hackshop.ultimate_unicorn.entity.horses.parts.powers.Powers;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Redirect;

/**
 * A walking Nightmare (Ultimate Unicorn Mod) sets the block at its feet to hoof fire without checking what is there,
 * so anything smaller than a full block it walks through (fence gates, stonecutters, garden pots, slabs, carpets,
 * flowers, torches...) was deleted. handleWalkingEffects' setBlockAndUpdate (Level.m_46597_) now only places the
 * fire into empty air (BlockState.isAir = m_60795_).
 */
@Mixin(value = Powers.class, remap = false)
public abstract class NightmareWalkFireMixin {
    @Redirect(method = "handleWalkingEffects", remap = false, at = @At(value = "INVOKE", remap = false,
            target = "Lnet/minecraft/world/level/Level;m_46597_(Lnet/minecraft/core/BlockPos;Lnet/minecraft/world/level/block/state/BlockState;)Z"))
    private boolean fotfmail$fireOnlyInAir(Level level, BlockPos pos, BlockState fire) {
        if (!level.m_8055_(pos).m_60795_()) {
            return false;
        }
        return level.m_46597_(pos, fire);
    }
}
