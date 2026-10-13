package fotfskills.mixin;

import net.minecraft.client.renderer.entity.LivingEntityRenderer;
import net.minecraft.client.renderer.entity.layers.RenderLayer;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Invoker;

/** LivingEntityRenderer.addLayer (m_115326_), protected at compile time. Used by client/DaleEarsLayer. */
@Mixin(value = LivingEntityRenderer.class, remap = false)
public interface LivingEntityRendererInvoker {
    @Invoker(value = "m_115326_", remap = false)
    boolean fotfskills$addLayer(RenderLayer<?, ?> layer);
}
