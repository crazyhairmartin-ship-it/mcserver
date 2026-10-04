package fotfskills.mixin;

import fotfskills.perk.Irrigation;
import fotfskills.world.IrrigatedFarmland;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.tags.FluidTags;
import net.minecraft.world.level.LevelReader;
import net.minecraft.world.level.block.FarmBlock;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * Irrigator: when vanilla finds no water within 4 blocks of farmland a player tilled, look further by their rank
 * (same height span as the pack's water-below rule: one block below to one above).
 */
@Mixin(value = FarmBlock.class, remap = false)
public abstract class FarmBlockIrrigatorMixin {
    @Inject(method = "m_53258_", remap = false, cancellable = true, at = @At("RETURN"))
    private static void fotfskills$irrigated(LevelReader reader, BlockPos pos, CallbackInfoReturnable<Boolean> cir) {
        if (cir.getReturnValueZ() || !(reader instanceof ServerLevel level)) {
            return;
        }
        int rank = IrrigatedFarmland.of(level).rank(pos);
        if (rank <= 0) {
            return;
        }
        int reach = Irrigation.reach(rank);
        for (BlockPos p : BlockPos.m_121940_(pos.m_7918_(-reach, -1, -reach), pos.m_7918_(reach, 1, reach))) {
            if (level.m_6425_(p).m_205070_(FluidTags.f_13131_)) {
                cir.setReturnValue(true);
                return;
            }
        }
    }
}
