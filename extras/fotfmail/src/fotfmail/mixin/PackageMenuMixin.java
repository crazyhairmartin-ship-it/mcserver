package fotfmail.mixin;

import com.chaosthedude.endermail.gui.container.PackageMenu;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.Constant;
import org.spongepowered.asm.mixin.injection.ModifyConstant;

/**
 * The package's 5 slots start at x 8 (left, like the mailbox's 3) instead of 44 (centred), leaving room on the right
 * for the recipient box (PackageScreenMixin). Slots are placed at 44 + i * 18 in the menu's constructor; this changes
 * the 44. The GUI texture's slot frames moved to match (kubejs/assets/endermail/textures/gui/package.png).
 */
@Mixin(PackageMenu.class)
public abstract class PackageMenuMixin {
    @ModifyConstant(method = "<init>(ILnet/minecraft/world/entity/player/Inventory;Lnet/minecraft/world/Container;)V",
            constant = @Constant(intValue = 44), remap = false)
    private int fotfmail$slotsOnTheLeft(int x) {
        return 8;
    }
}
