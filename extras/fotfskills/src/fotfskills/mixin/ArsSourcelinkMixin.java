package fotfskills.mixin;

import fotfskills.world.RankedBlocks;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.block.entity.BlockEntity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.ModifyVariable;

/** Sourcecraft: a sourcelink placed by a player with the perk makes 10% more source per rank (getManaEvent's amount). */
@Pseudo
@Mixin(targets = "com.hollingsworth.arsnouveau.common.block.tile.SourcelinkTile", remap = false)
public abstract class ArsSourcelinkMixin {
    @ModifyVariable(method = "getManaEvent", at = @At("HEAD"), argsOnly = true, ordinal = 0, remap = false, require = 0)
    private int fotfskills$moreSource(int amount) {
        BlockEntity tile = (BlockEntity) (Object) this;
        if (!(tile.m_58904_() instanceof ServerLevel level) || amount <= 0) {
            return amount;
        }
        int rank = RankedBlocks.of(level, RankedBlocks.SOURCELINKS).rank(tile.m_58899_());
        return rank <= 0 ? amount : amount + Math.round(amount * rank * 0.1f);
    }
}
