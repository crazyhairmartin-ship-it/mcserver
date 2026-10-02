package fotfmail.mixin;

import com.hackshop.ultimate_unicorn.blocks.NightmareFireBlock;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * The fire Nightmares (Ultimate Unicorn Mod) leave where they step is just a short-lived flicker: it never spreads
 * or burns anything, and goes out after a second or two. Its tick (m_213897_) is replaced: it goes out if it can't
 * stay where it is or on a 1-in-3 roll, otherwise checks again in 6-9 game ticks. (The mod's own "gentle" fire only
 * stopped it burning blocks; it still jumped into nearby air and took a while to age out.) First tick: FireBlockMixin.
 */
@Mixin(NightmareFireBlock.class)
public abstract class NightmareFireBlockMixin {
    @Inject(method = "m_213897_", at = @At("HEAD"), cancellable = true, remap = false)
    private void fotfmail$flickerOut(BlockState state, ServerLevel level, BlockPos pos, RandomSource random, CallbackInfo ci) {
        ci.cancel();
        if (!state.m_60710_(level, pos) || random.m_188503_(3) == 0) {
            level.m_7471_(pos, false);
            return;
        }
        level.m_186460_(pos, (Block) (Object) this, 6 + random.m_188503_(4));
    }
}
