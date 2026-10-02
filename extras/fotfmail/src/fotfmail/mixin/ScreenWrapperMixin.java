package fotfmail.mixin;

import com.chaosthedude.endermail.gui.ScreenWrapper;
import net.minecraft.core.BlockPos;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * No more stamping a placed package with a held stamp (Ender Mail's coordinates/ID screen): packages are sent with the
 * recipient box on the package's own screen, to mailboxes only. Right-clicking with a stamp just opens the package.
 */
@Mixin(ScreenWrapper.class)
public abstract class ScreenWrapperMixin {
    @Inject(method = "openStampScreen", at = @At("HEAD"), cancellable = true, remap = false)
    private static void fotfmail$noStampScreen(Level level, Player player, BlockPos pos, CallbackInfo ci) {
        ci.cancel();
    }
}
