package fotfmail.mixin;

import net.minecraft.client.gui.screens.inventory.AbstractContainerScreen;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Accessor;

/** A container screen's left/top position (f_97735_ / f_97736_, protected), for placing extra buttons. */
@Mixin(AbstractContainerScreen.class)
public interface AbstractContainerScreenAccessor {
    @Accessor(value = "f_97735_", remap = false)
    int fotfmail$leftPos();

    @Accessor(value = "f_97736_", remap = false)
    int fotfmail$topPos();
}
