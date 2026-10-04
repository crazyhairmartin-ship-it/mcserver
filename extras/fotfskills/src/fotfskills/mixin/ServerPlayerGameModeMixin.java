package fotfskills.mixin;

import fotfskills.perk.BlockPerks;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.server.level.ServerPlayerGameMode;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * Gathering XP and extra drops only for blocks a player really destroyed: destroyBlock (m_9280_) returns true once the
 * block is gone (claims, spawn protection and cancelled BreakEvents return false). The state, block entity and tool
 * are captured at HEAD because the break removes them (and may break the tool).
 */
@Mixin(value = ServerPlayerGameMode.class, remap = false)
public abstract class ServerPlayerGameModeMixin {
    @Shadow(remap = false)
    protected ServerLevel f_9244_;
    @Shadow(remap = false)
    @Final
    protected ServerPlayer f_9245_;

    @Unique
    private BlockState fotfskills$state;
    @Unique
    private BlockEntity fotfskills$blockEntity;
    @Unique
    private ItemStack fotfskills$tool;

    @Inject(method = "m_9280_", at = @At("HEAD"), remap = false)
    private void fotfskills$before(BlockPos pos, CallbackInfoReturnable<Boolean> cir) {
        fotfskills$state = f_9244_.m_8055_(pos);
        fotfskills$blockEntity = f_9244_.m_7702_(pos);
        fotfskills$tool = f_9245_.m_21205_().m_41777_();
    }

    @Inject(method = "m_9280_", at = @At("RETURN"), remap = false)
    private void fotfskills$after(BlockPos pos, CallbackInfoReturnable<Boolean> cir) {
        BlockState state = fotfskills$state;
        fotfskills$state = null;
        if (cir.getReturnValueZ() && state != null) {
            BlockPerks.onBroken(f_9245_, f_9244_, pos, state, fotfskills$blockEntity, fotfskills$tool);
        }
        fotfskills$blockEntity = null;
        fotfskills$tool = null;
    }
}
