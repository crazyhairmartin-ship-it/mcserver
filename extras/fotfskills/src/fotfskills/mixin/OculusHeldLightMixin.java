package fotfskills.mixin;

import fotfskills.compat.BackpackLantern;
import net.minecraft.client.player.LocalPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.item.ItemStack;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Redirect;

/**
 * Shaders' held-item light (Complementary etc.) also lights up the lantern hanging off the backpack. Shaders only know
 * two held lights (one per hand), so the lantern takes the place of a hand holding nothing that glows: the off-hand
 * first, else the main hand when the off-hand already glows. It then lights (and is coloured) exactly like a held
 * lantern. A light in both hands leaves no room for it.
 */
@Mixin(targets = "net.irisshaders.iris.uniforms.IdMapUniforms$HeldItemSupplier", remap = false)
public abstract class OculusHeldLightMixin {
    @Shadow
    @Final
    private InteractionHand hand;

    @Redirect(method = "update", remap = false, at = @At(value = "INVOKE",
            target = "Lnet/minecraft/client/player/LocalPlayer;m_21120_(Lnet/minecraft/world/InteractionHand;)Lnet/minecraft/world/item/ItemStack;"))
    private ItemStack fotfskills$backpackLantern(LocalPlayer player, InteractionHand which) {
        ItemStack held = player.m_21120_(which);
        if (glows(player, held)) {
            return held;
        }
        if (hand == InteractionHand.MAIN_HAND && !glows(player, player.m_21120_(InteractionHand.OFF_HAND))) {
            return held;                                                // the off-hand carries the lantern instead
        }
        ItemStack lantern = BackpackLantern.lantern(player);
        return lantern.m_41619_() ? held : lantern;
    }

    private static boolean glows(LocalPlayer player, ItemStack stack) {
        return !stack.m_41619_()
                && ((net.irisshaders.iris.api.v0.item.IrisItemLightProvider) stack.m_41720_()).getLightEmission(player, stack) > 0;
    }
}
