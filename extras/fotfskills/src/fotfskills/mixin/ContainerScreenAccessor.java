package fotfskills.mixin;

import net.minecraft.client.gui.screens.inventory.AbstractContainerScreen;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Accessor;

/** Where a container screen's panel is drawn (the skill buffs button sits beside the inventory). */
@Mixin(value = AbstractContainerScreen.class, remap = false)
public interface ContainerScreenAccessor {
    @Accessor(value = "f_97735_", remap = false)
    int fotfskills$left();

    @Accessor(value = "f_97736_", remap = false)
    int fotfskills$top();

    @Accessor(value = "f_97726_", remap = false)
    int fotfskills$width();
}
