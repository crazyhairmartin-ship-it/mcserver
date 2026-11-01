package fotfmail.mixin;

import com.teammetallurgy.aquaculture.block.blockentity.TackleBoxBlockEntity;
import com.teammetallurgy.aquaculture.inventory.container.TackleBoxContainer;
import fotfmail.HandTackleBox;
import net.minecraft.core.BlockPos;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.inventory.ClickType;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.entity.BlockEntity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.Redirect;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * Lets Aquaculture's tackle box menu run on a box held in the hand (HandTackleBox): its block entity lookup finds the
 * stand-in at HandTackleBox.POS, and while it's that stand-in the menu stays open as long as the box is held (not
 * while a tackle box block is nearby) and the box's own inventory slot is locked.
 */
@Mixin(TackleBoxContainer.class)
public abstract class TackleBoxContainerMixin {
    @Shadow(remap = false)
    public TackleBoxBlockEntity tackleBox;

    @Redirect(method = "<init>", remap = false, at = @At(value = "INVOKE", remap = false,
            target = "Lnet/minecraft/world/level/Level;m_7702_(Lnet/minecraft/core/BlockPos;)Lnet/minecraft/world/level/block/entity/BlockEntity;"))
    private BlockEntity fotfmail$handBox(Level level, BlockPos pos) {
        return HandTackleBox.lookup(level, pos);
    }

    @Inject(method = "m_6875_", at = @At("HEAD"), cancellable = true, remap = false)
    private void fotfmail$heldStillValid(Player player, CallbackInfoReturnable<Boolean> cir) {
        if (tackleBox instanceof HandTackleBox box) {
            cir.setReturnValue(box.stillValid(player));
        }
    }

    @Inject(method = "m_150399_", at = @At("HEAD"), cancellable = true, remap = false)
    private void fotfmail$lockHeldBox(int slot, int button, ClickType type, Player player, CallbackInfo ci) {
        if (tackleBox instanceof HandTackleBox box && box.blocksClick(slot, button, type)) {
            ci.cancel();
        }
    }
}
