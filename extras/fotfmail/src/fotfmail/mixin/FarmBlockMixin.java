package fotfmail.mixin;

import net.minecraft.world.level.block.FarmBlock;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.ModifyArg;

/**
 * Farmland also gets wet from water one block below it. isNearWater (m_53258_) scans
 * pos.offset(-4, 0, -4) .. pos.offset(4, 1, 4); this lowers the first corner's y from 0 to -1, so the scan covers
 * 4 blocks sideways from one block below the farmland to one above.
 */
@Mixin(FarmBlock.class)
public abstract class FarmBlockMixin {
    @ModifyArg(method = "m_53258_", remap = false, index = 1,
            at = @At(value = "INVOKE", target = "Lnet/minecraft/core/BlockPos;m_7918_(III)Lnet/minecraft/core/BlockPos;",
                    ordinal = 0, remap = false))
    private static int fotfmail$waterBelowCounts(int y) {
        return -1;
    }
}
