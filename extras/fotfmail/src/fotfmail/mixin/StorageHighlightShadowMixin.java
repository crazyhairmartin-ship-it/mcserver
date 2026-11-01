package fotfmail.mixin;

import com.mojang.blaze3d.vertex.PoseStack;
import fotfmail.CollarEffectTiming;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * Obscura's Simple Storage outlines (Item Locator, Highlight Connected Inventories, frame label boxes) aren't drawn in
 * a shader's shadow pass, where they showed up as stray boxes fixed on screen, like the Shadow Hands
 * (CollarEffectTiming.inShaderShadowPass). The real outlines still draw in the normal pass. Dylan, 2026-11-01.
 */
@Mixin(targets = {"com.obscura.storage.client.ItemLocatorClient", "com.obscura.storage.client.FrameLabelsClient"},
        remap = false)
public abstract class StorageHighlightShadowMixin {
    @Inject(method = {"render(Lcom/mojang/blaze3d/vertex/PoseStack;)V", "drawBoxes(Lcom/mojang/blaze3d/vertex/PoseStack;)V"},
            at = @At("HEAD"), cancellable = true, remap = false, require = 0)
    private static void fotfmail$notInShadowPass(PoseStack pose, CallbackInfo ci) {
        if (CollarEffectTiming.inShaderShadowPass()) {
            ci.cancel();
        }
    }
}
