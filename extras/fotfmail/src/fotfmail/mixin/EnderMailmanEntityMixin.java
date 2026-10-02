package fotfmail.mixin;

import com.chaosthedude.endermail.entity.EnderMailmanEntity;
import net.minecraft.core.NonNullList;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.common.extensions.IForgeEntity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * A mail carrier sent by fotfmail (persistent data flag "fotfmail_letter") drops the letter itself into the
 * mailbox, instead of the package item Ender Mail normally wraps the contents in.
 */
@Mixin(EnderMailmanEntity.class)
public abstract class EnderMailmanEntityMixin {
    @Inject(method = "getPackageStack", at = @At("HEAD"), cancellable = true, remap = false)
    private void fotfmail$deliverLetterItself(CallbackInfoReturnable<ItemStack> cir) {
        EnderMailmanEntity self = (EnderMailmanEntity) (Object) this;
        NonNullList<ItemStack> contents = self.getContents();
        if (((IForgeEntity) (Object) self).getPersistentData().m_128471_("fotfmail_letter") && !contents.isEmpty() && !contents.get(0).m_41619_()) {
            cir.setReturnValue(contents.get(0).m_41777_());
        }
    }
}
