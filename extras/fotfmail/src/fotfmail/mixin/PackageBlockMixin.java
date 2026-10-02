package fotfmail.mixin;

import com.chaosthedude.endermail.block.PackageBlock;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;
import org.spongepowered.asm.mixin.Mixin;

/**
 * Ender Mail's package, drawn here as a little chest with a stamp slapped on (kubejs/assets/endermail): chest-sized
 * outline/collision (getShape = m_5940_) and no occlusion (m_7952_), so neighbouring blocks still draw their faces.
 */
@Mixin(PackageBlock.class)
public abstract class PackageBlockMixin {
    private static final VoxelShape FOTFMAIL_CHEST = Block.m_49796_(1, 0, 1, 15, 14, 15);

    public VoxelShape m_7952_(BlockState state, BlockGetter level, BlockPos pos) {
        return Shapes.m_83040_();
    }

    public VoxelShape m_5940_(BlockState state, BlockGetter level, BlockPos pos, CollisionContext context) {
        return FOTFMAIL_CHEST;
    }
}
