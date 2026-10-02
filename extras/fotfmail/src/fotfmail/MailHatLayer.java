package fotfmail;

import com.chaosthedude.endermail.client.render.model.EnderMailmanModel;
import com.chaosthedude.endermail.entity.EnderMailmanEntity;
import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.model.geom.PartPose;
import net.minecraft.client.model.geom.builders.CubeListBuilder;
import net.minecraft.client.model.geom.builders.LayerDefinition;
import net.minecraft.client.model.geom.builders.MeshDefinition;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.client.renderer.entity.RenderLayerParent;
import net.minecraft.client.renderer.entity.layers.RenderLayer;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.resources.ResourceLocation;

/** A mail carrier's cap (navy crown, black visor, gold badge) on Ender Mail's enderman, following its head. */
final class MailHatLayer extends RenderLayer<EnderMailmanEntity, EnderMailmanModel> {
    private static final ResourceLocation TEXTURE = new ResourceLocation(FotfMail.MODID, "textures/entity/mail_hat.png");
    private final ModelPart hat;

    MailHatLayer(RenderLayerParent<EnderMailmanEntity, EnderMailmanModel> parent) {
        super(parent);
        MeshDefinition mesh = new MeshDefinition();
        mesh.m_171576_().m_171599_("hat", CubeListBuilder.m_171558_()
                .m_171514_(0, 0).m_171481_(-4.5F, -11.0F, -4.5F, 9.0F, 3.0F, 9.0F)    // crown, on top of the head
                .m_171514_(0, 12).m_171481_(-4.5F, -8.5F, -7.5F, 9.0F, 0.5F, 3.0F)   // visor, sticking out the front
                .m_171514_(0, 17).m_171481_(-1.0F, -10.5F, -4.75F, 2.0F, 2.0F, 0.25F), // badge on the crown's front
                PartPose.f_171404_);
        hat = LayerDefinition.m_171565_(mesh, 64, 32).m_171564_().m_171324_("hat");
    }

    @Override
    public void m_6494_(PoseStack pose, MultiBufferSource buffers, int light, EnderMailmanEntity carrier,
                        float limbSwing, float limbSwingAmount, float partialTick, float ageInTicks, float headYaw, float headPitch) {
        pose.m_85836_();
        m_117386_().f_102808_.m_104299_(pose);
        hat.m_104301_(pose, buffers.m_6299_(RenderType.m_110458_(TEXTURE)), light, OverlayTexture.f_118083_);
        pose.m_85849_();
    }
}
