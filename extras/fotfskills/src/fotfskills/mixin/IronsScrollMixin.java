package fotfskills.mixin;

import fotfskills.compat.ThirdPerson;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** Reading a scroll: face the third-person crosshair first (client side). See ThirdPerson. */
@Pseudo
@Mixin(targets = "io.redspace.ironsspellbooks.item.Scroll", remap = false)
public abstract class IronsScrollMixin {
    @Inject(method = "m_7203_", at = @At("HEAD"), remap = false)
    private void fotfskills$faceCrosshair(Level level, Player player, InteractionHand hand,
                                          CallbackInfoReturnable<InteractionResultHolder<ItemStack>> cir) {
        if (level.m_5776_()) {
            ThirdPerson.faceCrosshair();
        }
    }
}
