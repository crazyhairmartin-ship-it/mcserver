package fotfskills.mixin;

import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.Entity;
import net.minecraftforge.registries.ForgeRegistries;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * Fay's Fairies glow: their GeckoLib renderer draws them at full brightness, so they shine in dark forests. The render
 * call is redone once with full light (the fairies' own renderers don't take a light override).
 */
@Pseudo
@Mixin(targets = "software.bernie.geckolib.renderer.GeoEntityRenderer", remap = false)
public abstract class FairyGlowMixin {
    @Unique
    private static final int FULL_BRIGHT = 0xF000F0;
    @Unique
    private static boolean fotfskills$glowing;

    @Inject(method = "m_7392_", at = @At("HEAD"), cancellable = true, remap = false, require = 0)
    private void fotfskills$fairyGlow(Entity entity, float yaw, float partialTick, PoseStack poseStack, MultiBufferSource buffers,
                                      int packedLight, CallbackInfo ci) {
        if (fotfskills$glowing || packedLight == FULL_BRIGHT) {
            return;
        }
        ResourceLocation id = ForgeRegistries.ENTITY_TYPES.getKey(entity.m_6095_());
        if (id == null || !id.m_135827_().equals("fays_fairies")) {
            return;
        }
        fotfskills$glowing = true;
        try {
            ((net.minecraft.client.renderer.entity.EntityRenderer<Entity>) (Object) this)
                    .m_7392_(entity, yaw, partialTick, poseStack, buffers, FULL_BRIGHT);
        } finally {
            fotfskills$glowing = false;
        }
        ci.cancel();
    }
}
