package fotfskills.mixin;

import java.util.Set;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.inventory.InventoryScreen;
import net.minecraft.world.entity.LivingEntity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Redirect;

/**
 * Book of Familiars' portrait draws a freshly made copy of the familiar that has never touched the ground, so Wings
 * Horns & Hooves mounts flapped or reared on a loop. Their copies get the mod's own NoAnimation flag (what its display
 * horses use: a still pose), every copy is put on the ground, and winged ones are drawn smaller (the book sizes the
 * portrait by the body, not the wings).
 */
@Mixin(targets = "net.fayebeard.bookffamiliars.GUI.FamiliarBookScreen", remap = false)
public abstract class FamiliarPreviewMixin {
    private static final Set<String> WINGED = Set.of("com.hackshop.ultimate_unicorn.entity.horses.Pegasus",
            "com.hackshop.ultimate_unicorn.entity.horses.Nightmare");
    private static final float WINGED_SCALE = 0.6f;
    private static java.lang.reflect.Field noAnimation;
    private static boolean noAnimationLooked;

    @Redirect(method = "renderEntityPreview", remap = false, at = @At(value = "INVOKE",
            target = "Lnet/minecraft/client/gui/screens/inventory/InventoryScreen;m_274545_(Lnet/minecraft/client/gui/GuiGraphics;IIIFFLnet/minecraft/world/entity/LivingEntity;)V"))
    private void fotfskills$groundedPortrait(GuiGraphics graphics, int x, int y, int scale, float mouseX, float mouseY,
                                             LivingEntity entity) {
        entity.m_6853_(true);
        freeze(entity);
        if (WINGED.contains(entity.getClass().getName())) {
            scale = Math.round(scale * WINGED_SCALE);
        }
        InventoryScreen.m_274545_(graphics, x, y, scale, mouseX, mouseY, entity);
    }

    /** MagicalHorse.noAnimation = true (protected field, read by all its GeckoLib controllers). */
    private static void freeze(LivingEntity entity) {
        if (!noAnimationLooked) {
            noAnimationLooked = true;
            try {
                noAnimation = Class.forName("com.hackshop.ultimate_unicorn.entity.horses.MagicalHorse").getDeclaredField("noAnimation");
                noAnimation.setAccessible(true);
            } catch (ReflectiveOperationException | RuntimeException e) {
                noAnimation = null;
            }
        }
        if (noAnimation != null && noAnimation.getDeclaringClass().isInstance(entity)) {
            try {
                noAnimation.setBoolean(entity, true);
            } catch (IllegalAccessException e) {
                // leave it animated
            }
        }
    }
}
