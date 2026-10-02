package fotfmail.mixin;

import com.chaosthedude.endermail.block.LockerBlock;
import fotfmail.FotfMail;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** Adds the "wood" property to Ender Mail's locker (createBlockStateDefinition = m_7926_). */
@Mixin(LockerBlock.class)
public abstract class LockerBlockMixin {
    @Inject(method = "m_7926_", at = @At("TAIL"), remap = false)
    private void fotfmail$addWood(StateDefinition.Builder<Block, BlockState> builder, CallbackInfo ci) {
        builder.m_61104_(FotfMail.WOOD);
    }
}
