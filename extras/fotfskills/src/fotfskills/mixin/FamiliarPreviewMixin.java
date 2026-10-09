package fotfskills.mixin;

import java.util.Set;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.inventory.InventoryScreen;
import net.minecraft.world.entity.LivingEntity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Redirect;

/**
 * Book of Familiars' portrait draws a freshly made copy of the familiar that has never touched the ground, so winged
 * mounts (Wings Horns & Hooves pegasi and nightmares) show their flying pose, wings spread past the frame. The copy is
 * put on the ground first, and winged ones are drawn smaller (the book sizes the portrait by the body, not the wings).
 */
@Mixin(targets = "net.fayebeard.bookffamiliars.GUI.FamiliarBookScreen", remap = false)
public abstract class FamiliarPreviewMixin {
    private static final Set<String> WINGED = Set.of("com.hackshop.ultimate_unicorn.entity.horses.Pegasus",
            "com.hackshop.ultimate_unicorn.entity.horses.Nightmare");
    private static final float WINGED_SCALE = 0.6f;

    @Redirect(method = "renderEntityPreview", remap = false, at = @At(value = "INVOKE",
            target = "Lnet/minecraft/client/gui/screens/inventory/InventoryScreen;m_274545_(Lnet/minecraft/client/gui/GuiGraphics;IIIFFLnet/minecraft/world/entity/LivingEntity;)V"))
    private void fotfskills$groundedPortrait(GuiGraphics graphics, int x, int y, int scale, float mouseX, float mouseY,
                                             LivingEntity entity) {
        entity.m_6853_(true);
        if (WINGED.contains(entity.getClass().getName())) {
            scale = Math.round(scale * WINGED_SCALE);
        }
        InventoryScreen.m_274545_(graphics, x, y, scale, mouseX, mouseY, entity);
    }
}
