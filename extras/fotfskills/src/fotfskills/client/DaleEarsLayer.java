package fotfskills.client;

import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import fotfskills.mixin.LivingEntityRendererInvoker;
import fotfskills.mixin.WolfModelAccessor;
import java.util.EnumSet;
import java.util.List;
import java.util.Map;
import net.minecraft.client.model.WolfModel;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.entity.LivingEntityRenderer;
import net.minecraft.client.renderer.entity.RenderLayerParent;
import net.minecraft.client.renderer.entity.layers.RenderLayer;
import net.minecraft.core.Direction;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.animal.Wolf;
import net.minecraftforge.client.event.EntityRenderersEvent;

/**
 * Dale (any wolf named Dale) has floppy hound ears, drawn as an extra layer on the wolf like the collar: two ears
 * (dale_ears.png, his ear pixels at the vanilla ear spot 16,14) attached to the head, so they follow every head
 * movement, tipping outward and hanging about twice as long. The upright vanilla ears are see-through in his coat
 * (tools/skins/make_dale.py). Drawn this way rather than by changing the wolf model because Entity Model Features keeps
 * its own copy of every model part and puts it back each frame.
 */
public final class DaleEarsLayer extends RenderLayer<Wolf, WolfModel<Wolf>> {
    private static final ResourceLocation EARS = new ResourceLocation("fotfskills", "textures/entity/dale_ears.png");
    private static final float DROOP = 2.6f;               // about 150 degrees: tipped over, hanging outward
    private static final float LENGTH = 2.2f;
    private final ModelPart right = ear();
    private final ModelPart left = ear();

    public DaleEarsLayer(RenderLayerParent<Wolf, WolfModel<Wolf>> parent) {
        super(parent);
    }

    @SuppressWarnings("unchecked")
    public static void onAddLayers(EntityRenderersEvent.AddLayers event) {
        LivingEntityRenderer<Wolf, WolfModel<Wolf>> renderer = event.getRenderer(EntityType.f_20499_);
        if (renderer != null) {
            ((LivingEntityRendererInvoker) renderer).fotfskills$addLayer(new DaleEarsLayer(renderer));
        }
    }

    @Override
    public void m_6494_(PoseStack pose, MultiBufferSource buffers, int light, Wolf wolf, float limbSwing, float limbAmount,
                        float partialTick, float age, float yaw, float pitch) {
        if (wolf.m_20145_() || !wolf.m_8077_() || wolf.m_7770_() == null
                || !wolf.m_7770_().getString().trim().equalsIgnoreCase("dale")) {
            return;
        }
        WolfModelAccessor model = (WolfModelAccessor) (Object) m_117386_();
        pose.m_85836_();
        model.fotfskills$head().m_104299_(pose);
        model.fotfskills$realHead().m_104299_(pose);
        VertexConsumer buffer = buffers.m_6299_(RenderType.m_110458_(EARS));
        int overlay = LivingEntityRenderer.m_115338_(wolf, 0);
        place(right, -1, -DROOP);
        place(left, 3, DROOP);
        right.m_104301_(pose, buffer, light, overlay);
        left.m_104301_(pose, buffer, light, overlay);
        pose.m_85849_();
    }

    /** The vanilla ear box (2x2x1, texture 16,14 on the 64x32 wolf sheet), standing up from its pivot. */
    private static ModelPart ear() {
        ModelPart.Cube cube = new ModelPart.Cube(16, 14, -1, -2, 0, 2, 2, 1, 0, 0, 0, false, 64, 32, EnumSet.allOf(Direction.class));
        return new ModelPart(List.of(cube), Map.of());
    }

    /** Pivot where the vanilla ear meets the head (ear boxes sit at x -2..0 / 2..4, y -5..-3, z 0..1), then droop. */
    private static void place(ModelPart ear, float x, float droop) {
        ear.f_104200_ = x;
        ear.f_104201_ = -3;
        ear.f_104202_ = 0;
        ear.f_104203_ = 0;
        ear.f_104204_ = 0;
        ear.f_104205_ = droop;
        ear.f_233553_ = 1;
        ear.f_233554_ = LENGTH;
        ear.f_233555_ = 1;
    }
}
