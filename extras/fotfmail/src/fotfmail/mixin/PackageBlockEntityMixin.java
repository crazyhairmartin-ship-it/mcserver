package fotfmail.mixin;

import com.chaosthedude.endermail.block.PackageBlock;
import com.chaosthedude.endermail.block.entity.PackageBlockEntity;
import fotfmail.FotfMail;
import fotfmail.Mail;
import fotfmail.PackageInfoPacket;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.player.Player;
import net.minecraftforge.network.PacketDistributor;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraftforge.common.extensions.IForgeBlockEntity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * A delivered package that's been emptied disappears when you close its screen (stopOpen = m_5785_), breaking like a
 * chest (particles + sound). Delivered = marked "fotfmail_received" when a carrier drops it in a mailbox
 * (EnderMailmanEntityMixin), or a stamped package (one a carrier set down, or one just sent that the sender emptied).
 */
@Mixin(PackageBlockEntity.class)
public abstract class PackageBlockEntityMixin {
    /** Opening the package (startOpen = m_5856_) tells the player's screen what to show (PackageInfoPacket). */
    @Inject(method = "m_5856_", at = @At("HEAD"), remap = false)
    private void fotfmail$tellScreen(Player player, CallbackInfo ci) {
        PackageBlockEntity self = (PackageBlockEntity) (Object) this;
        if (!(player instanceof ServerPlayer serverPlayer) || !(self.m_58904_() instanceof ServerLevel server)) {
            return;
        }
        BlockPos pos = self.m_58899_();
        CompoundTag data = ((IForgeBlockEntity) self).getPersistentData();
        String from = data.m_128471_("fotfmail_received") ? data.m_128461_(Mail.FROM_TAG) : "";
        if (data.m_128471_("fotfmail_received") && from.isEmpty()) {
            from = "?";
        }
        BlockState state = server.m_8055_(pos);
        String sentTo = from.isEmpty() && state.m_60734_() instanceof PackageBlock block && block.isStamped(state)
                ? String.valueOf(PackageBlock.getLockerID(server, pos)) : "";
        FotfMail.NETWORK.send(PacketDistributor.PLAYER.with(() -> serverPlayer), new PackageInfoPacket(pos, from, sentTo));
    }

    @Inject(method = "m_5785_", at = @At("RETURN"), remap = false)
    private void fotfmail$vanishWhenClosedEmpty(CallbackInfo ci) {
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
