package fotfmail.mixin;

import net.minecraft.core.BlockPos;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import net.satisfy.farm_and_charm.core.block.StoveBlock;
import net.satisfy.farm_and_charm.core.block.entity.StoveBlockEntity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * Farm & Charm's Baker's Stove shows flames only while it's burning fuel. Its own rule is "lit while burning, or once
 * it has ever burned" (burnTime == 0 but burnTimeTotal > 0), so a stove that baked once stayed lit forever. Pots and
 * pans on top don't care: they heat from the allows_cooking tag, not from LIT. Dylan, 2026-11-01.
 */
@Mixin(value = StoveBlockEntity.class, remap = false)
public abstract class BakersStoveLitMixin {
    @Shadow(remap = false)
    protected int burnTime;

    @Inject(method = "tick", at = @At("TAIL"), remap = false)
    private void fotfmail$litOnlyWhileBurning(Level level, BlockPos pos, BlockState state, StoveBlockEntity stove,
            CallbackInfo ci) {
        if (level.f_46443_) {
            return;
        }
        BlockState now = level.m_8055_(pos);
        boolean burning = burnTime > 0;
        if (now.m_61138_(StoveBlock.LIT) && now.m_61143_(StoveBlock.LIT) != burning) {
            level.m_7731_(pos, now.m_61124_(StoveBlock.LIT, burning), 3);
        }
    }
}
