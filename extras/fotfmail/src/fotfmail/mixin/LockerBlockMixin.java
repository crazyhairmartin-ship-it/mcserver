package fotfmail.mixin;

import com.chaosthedude.endermail.block.LockerBlock;
import fotfmail.FotfMail;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * Ender Mail's locker, drawn here as a birdhouse (kubejs/assets/endermail):
 * - adds the "wood" block state (createBlockStateDefinition = m_7926_)
 * - occlusion shape (m_7952_) empty, so neighbouring blocks don't hide their faces behind it (the locker was a full
 *   opaque cube, which left see-through holes around the birdhouse)
 * - outline/collision shape (m_5940_) is the birdhouse's post and house, turned with the mailbox
 */
@Mixin(LockerBlock.class)
public abstract class LockerBlockMixin {
    private static final VoxelShape FOTFMAIL_NORTH_SOUTH = Shapes.m_83110_(
            Block.m_49796_(6, 0, 6, 10, 5, 10), Block.m_49796_(3, 5, 2, 13, 16, 14));
    private static final VoxelShape FOTFMAIL_EAST_WEST = Shapes.m_83110_(
            Block.m_49796_(6, 0, 6, 10, 5, 10), Block.m_49796_(2, 5, 3, 14, 16, 13));

    @Inject(method = "m_7926_", at = @At("TAIL"), remap = false)
    private void fotfmail$addWood(StateDefinition.Builder<Block, BlockState> builder, CallbackInfo ci) {
        builder.m_61104_(FotfMail.WOOD);
    }

    public VoxelShape m_7952_(BlockState state, BlockGetter level, BlockPos pos) {
        return Shapes.m_83040_();
    }

    public VoxelShape m_5940_(BlockState state, BlockGetter level, BlockPos pos, CollisionContext context) {
        Direction facing = state.m_61143_(LockerBlock.FACING);
        return facing == Direction.EAST || facing == Direction.WEST ? FOTFMAIL_EAST_WEST : FOTFMAIL_NORTH_SOUTH;
    }
}
