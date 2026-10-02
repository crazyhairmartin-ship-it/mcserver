package fotfmail.mixin;

import com.chaosthedude.endermail.block.PackageBlock;
import com.chaosthedude.endermail.block.entity.PackageBlockEntity;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraftforge.common.extensions.IForgeBlockEntity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * A package that has been delivered disappears as soon as it's empty, breaking like a chest (particles + sound). Delivered = marked "fotfmail_received" when a
 * carrier drops it in a mailbox (EnderMailmanEntityMixin), or a stamped package (one a carrier set down, or one just
 * sent that the sender emptied again). Checked whenever items leave it, however they're taken (click = removeItem
 * m_7407_ / m_8016_, shift-click = setItem m_6836_), and when its screen is closed (stopOpen m_5785_).
 */
@Mixin(PackageBlockEntity.class)
public abstract class PackageBlockEntityMixin {
    @Inject(method = {"m_7407_", "m_8016_"}, at = @At("RETURN"), remap = false)
    private void fotfmail$afterTake(CallbackInfoReturnable<ItemStack> cir) {
        fotfmail$vanishIfLooted();
    }

    @Inject(method = {"m_6836_", "m_5785_"}, at = @At("RETURN"), remap = false)
    private void fotfmail$afterSetOrClose(CallbackInfo ci) {
        fotfmail$vanishIfLooted();
    }

    @Unique
    private void fotfmail$vanishIfLooted() {
        PackageBlockEntity self = (PackageBlockEntity) (Object) this;
        Level level = self.m_58904_();
        if (!(level instanceof ServerLevel server) || self.m_58901_() || !self.m_7983_()) {
            return;
        }
        BlockPos pos = self.m_58899_();
        BlockState state = server.m_8055_(pos);
        boolean stamped = state.m_60734_() instanceof PackageBlock block && block.isStamped(state);
        if (!stamped && !((IForgeBlockEntity) self).getPersistentData().m_128471_("fotfmail_received")) {
            return;
        }
        // Break effect as if a chest were broken there: chest particles and the wooden break sound (level event 2001).
        server.m_46796_(2001, pos, Block.m_49956_(Blocks.f_50087_.m_49966_()));
        server.m_7471_(pos, false);
    }
}
