package fotfmail;

import com.github.alexthe668.domesticationinnovation.client.render.LayerPetOverlays;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import com.mojang.math.Axis;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.entity.RenderLayerParent;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import software.bernie.geckolib.cache.object.BakedGeoModel;
import software.bernie.geckolib.core.animatable.GeoAnimatable;
import software.bernie.geckolib.renderer.GeoEntityRenderer;
import software.bernie.geckolib.renderer.layer.GeoRenderLayer;

/**
 * Domestication Innovation's collar enchantment effects (shadow hands, magnet, auras, blazing bars, lightning...)
 * on GeckoLib mobs (Critters & Companions, Naturalist, Ultimate Unicorn Mod). DI only adds its LayerPetOverlays to
 * vanilla-style LivingEntityRenderers; this runs the same layer from a GeckoLib render layer.
 *
 * GeckoLib renders layers from the entity's origin before its body rotation, so this applies the vanilla
 * LivingEntityRenderer transform first (body yaw, flip, -1.501 offset). DI's two model-redraw effects (immunity
 * frame glint, zombie pet overlay) need a vanilla model, so they stay off on these mobs (NO_MODEL draws nothing).
 */
final class PetOverlaysGeoLayer<T extends Entity & GeoAnimatable> extends GeoRenderLayer<T> {
    private final LayerPetOverlays overlays;

    PetOverlaysGeoLayer(GeoEntityRenderer<T> renderer) {
        super(renderer);
        overlays = new LayerPetOverlays(new Parent(renderer));
    }

    @Override
    public void render(PoseStack pose, T animatable, BakedGeoModel model, RenderType renderType, MultiBufferSource buffers,
                       VertexConsumer buffer, float partialTick, int light, int overlay) {
        if (!(animatable instanceof LivingEntity living)) {
            return;
        }
        pose.m_85836_();
        pose.m_252781_(Axis.f_252436_.m_252977_(180.0F - Mth.m_14189_(partialTick, living.f_20884_, living.f_20883_)));
        pose.m_85841_(-1.0F, -1.0F, 1.0F);
        pose.m_252880_(0.0F, -1.501F, 0.0F);
        overlays.m_6494_(pose, buffers, light, living, 0.0F, 0.0F, partialTick, living.f_19797_ + partialTick, 0.0F, 0.0F);
        pose.m_85849_();
    }

    /** What LayerPetOverlays asks its parent renderer for: the texture (zombie overlay sizing) and a model. */
    @SuppressWarnings({"rawtypes", "unchecked"})
    private static final class Parent implements RenderLayerParent {
        private static final EntityModel<Entity> NO_MODEL = new EntityModel<>() {
            @Override
            public void m_6973_(Entity entity, float a, float b, float c, float d, float e) {
            }

            @Override
            public void m_7695_(PoseStack pose, VertexConsumer buffer, int light, int overlay, float r, float g, float b, float a) {
            }
        };
        private final GeoEntityRenderer renderer;

        Parent(GeoEntityRenderer renderer) {
            this.renderer = renderer;
        }

        @Override
        public EntityModel m_7200_() {
            return NO_MODEL;
        }

        @Override
        public ResourceLocation m_5478_(Entity entity) {
            return renderer.getTextureLocation((GeoAnimatable) entity);
        }
    }
}
