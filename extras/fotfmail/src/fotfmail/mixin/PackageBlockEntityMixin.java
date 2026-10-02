package fotfmail.mixin;

import com.chaosthedude.endermail.block.entity.PackageBlockEntity;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraftforge.common.extensions.IForgeBlockEntity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * A package that was delivered (marked "fotfmail_received" by EnderMailmanEntityMixin when the carrier drops it in a
 * mailbox) disappears as soon as its last item is taken out. removeItem = m_7407_, removeItemNoUpdate = m_8016_.
 */
@Mixin(PackageBlockEntity.class)
public abstract class PackageBlockEntityMixin {
    @Inject(method = {"m_7407_", "m_8016_"}, at = @At("RETURN"), remap = false)
    private void fotfmail$vanishWhenLooted(CallbackInfoReturnable<ItemStack> cir) {
        PackageBlockEntity self = (PackageBlockEntity) (Object) this;
        Level level = self.m_58904_();
        if (!(level instanceof ServerLevel server) || !self.m_7983_()
                || !((IForgeBlockEntity) self).getPersistentData().m_128471_("fotfmail_received")) {
            return;
        }
        BlockPos pos = self.m_58899_();
        server.m_7471_(pos, false);
        server.m_5594_(null, pos, SoundEvents.f_11713_, SoundSource.BLOCKS, 0.8F, 0.8F);
        server.m_8767_(ParticleTypes.f_123759_, pos.m_123341_() + 0.5, pos.m_123342_() + 0.5, pos.m_123343_() + 0.5, 12, 0.3, 0.3, 0.3, 0.02);
    }
}
