package fotfskills.mixin;

import fotfskills.world.BanisterCorners;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.LevelAccessor;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.HorizontalDirectionalBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.EnumProperty;
import net.minecraft.world.level.block.state.properties.StairsShape;
import net.minecraft.world.level.material.Fluids;
import net.minecraft.world.phys.shapes.BooleanOp;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * Twilight Forest banisters (and Every Compat's, which use the same block class) turn corners like stairs: a "corner"
 * property set on placement and whenever a neighbour changes (see world/BanisterCorners). INNER = rails on the facing
 * edge and one side (an L), OUTER = just the corner post. Hitboxes follow: the union / overlap of the two straight
 * banisters. The corner models are built in game from the straight ones (client/BanisterCornerModels). Pseudo:
 * skipped without Twilight Forest.
 */
@Pseudo
@Mixin(targets = "twilightforest.block.BanisterBlock", remap = false)
public abstract class BanisterBlockMixin extends HorizontalDirectionalBlock {
    @Unique
    private static final EnumProperty<StairsShape> FOTF_CORNER = EnumProperty.m_61587_("corner", StairsShape.class);

    protected BanisterBlockMixin(Properties properties) {
        super(properties);
    }

    @Inject(method = "m_7926_", at = @At("TAIL"), remap = false)
    private void fotfskills$cornerProperty(StateDefinition.Builder<Block, BlockState> builder, CallbackInfo ci) {
        builder.m_61104_(FOTF_CORNER);
    }

    @Inject(method = "m_5573_", at = @At("RETURN"), cancellable = true, remap = false)
    private void fotfskills$cornerOnPlace(BlockPlaceContext context, CallbackInfoReturnable<BlockState> cir) {
        BlockState state = cir.getReturnValue();
        if (state != null && state.m_61138_(FOTF_CORNER)) {
            cir.setReturnValue(state.m_61124_(FOTF_CORNER, fotfskills$corner(state, context.m_43725_(), context.m_8083_())));
        }
    }

    /** BanisterBlock has no updateShape of its own: this one re-picks the corner (and keeps water flowing when waterlogged). */
    @Override
    public BlockState m_7417_(BlockState state, Direction direction, BlockState neighbour, LevelAccessor level,
                              BlockPos pos, BlockPos neighbourPos) {
        BlockState updated = super.m_7417_(state, direction, neighbour, level, pos, neighbourPos);
        if (updated.m_61138_(net.minecraft.world.level.block.state.properties.BlockStateProperties.f_61362_)
                && updated.m_61143_(net.minecraft.world.level.block.state.properties.BlockStateProperties.f_61362_)) {
            level.m_186469_(pos, Fluids.f_76193_, Fluids.f_76193_.m_6718_(level));
        }
        if (direction.m_122434_().m_122479_() && updated.m_61138_(FOTF_CORNER)) {
            updated = updated.m_61124_(FOTF_CORNER, fotfskills$corner(updated, level, pos));
        }
        return updated;
    }

    @Inject(method = "m_5940_", at = @At("RETURN"), cancellable = true, remap = false)
    private void fotfskills$cornerShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext ctx,
                                        CallbackInfoReturnable<VoxelShape> cir) {
        if (!state.m_61138_(FOTF_CORNER)) {
            return;
        }
        StairsShape corner = state.m_61143_(FOTF_CORNER);
        if (corner == StairsShape.STRAIGHT) {
            return;
        }
        Direction facing = state.m_61143_(f_54117_);
        boolean left = corner == StairsShape.INNER_LEFT || corner == StairsShape.OUTER_LEFT;
        Direction side = left ? facing.m_122428_() : facing.m_122427_();
        BlockState straight = state.m_61124_(FOTF_CORNER, StairsShape.STRAIGHT);
        VoxelShape front = this.m_5940_(straight, level, pos, ctx);
        VoxelShape beside = this.m_5940_(straight.m_61124_(f_54117_, side), level, pos, ctx);
        boolean inner = corner == StairsShape.INNER_LEFT || corner == StairsShape.INNER_RIGHT;
        cir.setReturnValue(inner ? Shapes.m_83110_(front, beside) : Shapes.m_83113_(front, beside, BooleanOp.f_82689_));
    }

    @Unique
    private StairsShape fotfskills$corner(BlockState state, BlockGetter level, BlockPos pos) {
        return BanisterCorners.shape(state.m_61143_(f_54117_), dir -> {
            BlockState other = level.m_8055_(pos.m_121945_(dir));
            return other.m_60734_() instanceof HorizontalDirectionalBlock && other.m_61138_(FOTF_CORNER)
                    ? other.m_61143_(f_54117_) : null;
        });
    }
}
