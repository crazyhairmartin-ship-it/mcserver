package fotfskills.mixin;

import io.redspace.ironsspellbooks.gui.scroll_forge.ScrollForgeScreen;
import java.util.List;
import net.minecraft.client.gui.Font;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.util.FormattedCharSequence;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.Redirect;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * Iron's Scroll Forge draws the hovered spell's tooltip while drawing its background, so the inventory's items were drawn
 * over it. The tooltip is held back and drawn after everything else.
 */
@Mixin(value = ScrollForgeScreen.class, remap = false)
public abstract class ScrollForgeTooltipMixin {
    @Unique private Font fotfskills$font;
    @Unique private List<FormattedCharSequence> fotfskills$lines;
    @Unique private int fotfskills$x;
    @Unique private int fotfskills$y;

    @Redirect(method = "renderSpellList", remap = false, at = @At(value = "INVOKE",
            target = "Lnet/minecraft/client/gui/GuiGraphics;m_280245_(Lnet/minecraft/client/gui/Font;Ljava/util/List;II)V"))
    private void fotfskills$later(GuiGraphics graphics, Font font, List<FormattedCharSequence> lines, int x, int y) {
        fotfskills$font = font;
        fotfskills$lines = lines;
        fotfskills$x = x;
        fotfskills$y = y;
    }

    @Inject(method = "m_88315_", remap = false, at = @At("TAIL"))
    private void fotfskills$onTop(GuiGraphics graphics, int mouseX, int mouseY, float partialTick, CallbackInfo ci) {
        if (fotfskills$lines != null) {
            graphics.m_280245_(fotfskills$font, fotfskills$lines, fotfskills$x, fotfskills$y);
            fotfskills$lines = null;
        }
    }
}
