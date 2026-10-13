package fotfmail.mixin;

import net.minecraft.client.gui.components.events.GuiEventListener;
import net.minecraft.client.gui.screens.Screen;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Invoker;

/** Screen.addRenderableWidget (m_142416_) is protected; used to add buttons to other mods' screens. */
@Mixin(Screen.class)
public interface ScreenAccessor {
    @Invoker(value = "m_142416_", remap = false)
    GuiEventListener fotfmail$addRenderableWidget(GuiEventListener widget);
}
