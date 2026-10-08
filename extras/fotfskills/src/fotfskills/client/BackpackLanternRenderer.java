package fotfskills.client;

import com.mojang.blaze3d.vertex.PoseStack;
import fotfskills.compat.BackpackLantern;
import net.minecraft.client.Minecraft;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.model.HumanoidModel;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.entity.RenderLayerParent;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraftforge.registries.ForgeRegistries;
import org.joml.Quaternionf;
import top.theillusivec4.curios.api.SlotContext;
import top.theillusivec4.curios.api.client.CuriosRendererRegistry;
import top.theillusivec4.curios.api.client.ICurioRenderer;

/**
 * Draws the lantern from the Curios Lantern slot hanging off the left side of the wearer's backpack, as the hanging
 * block model, swinging a little as they walk. Positions are in body-model pixels: the body box is x -4..4,
 * y 0..12 (down), z -2..2, and backpacks sit behind it.
 */
public final class BackpackLanternRenderer implements ICurioRenderer {
    // small packs and bags (Camping): at the hip
    private static final float HANG_X = 5.5f / 16;
    private static final float HANG_Y = 5f / 16;
    private static final float HANG_Z = 4.5f / 16;
    // Sophisticated Backpacks are wide and deep: hang it clear of the pack's side and lower
    private static final float BIG_X = 7.5f / 16;
    private static final float BIG_Y = 9f / 16;
    private static final float BIG_Z = 5f / 16;
    private static final float SCALE = 0.42f;

    /** The items in the curios:lantern tag (kubejs/data/curios/tags/items/lantern.json); tags aren't loaded yet here. */
    private static final String[] LANTERNS = {"minecraft:lantern", "minecraft:soul_lantern", "meadow:oil_lantern"};

    public static void registerAll() {
        for (String id : LANTERNS) {
            var item = ForgeRegistries.ITEMS.getValue(new net.minecraft.resources.ResourceLocation(id));
            if (item instanceof BlockItem) {
                CuriosRendererRegistry.register(item, BackpackLanternRenderer::new);
            }
        }
    }

    @Override
    public <T extends LivingEntity, M extends EntityModel<T>> void render(ItemStack stack, SlotContext slot, PoseStack pose,
            RenderLayerParent<T, M> parent, MultiBufferSource buffers, int light, float limbSwing, float limbSwingAmount,
            float partialTicks, float ageInTicks, float netHeadYaw, float headPitch) {
        LivingEntity wearer = slot.entity();
        ItemStack pack = BackpackLantern.backpack(wearer);
        if (!(stack.m_41720_() instanceof BlockItem item) || pack.m_41619_()
                || !(parent.m_7200_() instanceof HumanoidModel<?> model)) {
            return;
        }
        BlockState state = item.m_40614_().m_49966_();
        if (state.m_61138_(BlockStateProperties.f_61435_)) {
            state = state.m_61124_(BlockStateProperties.f_61435_, true);
        }
        pose.m_85836_();
        model.f_102810_.m_104299_(pose);                                    // follow the body (turning, sneaking)
        boolean big = "sophisticatedbackpacks".equals(ForgeRegistries.ITEMS.getKey(pack.m_41720_()).m_135827_());
        pose.m_252880_(big ? BIG_X : HANG_X, big ? BIG_Y : HANG_Y, big ? BIG_Z : HANG_Z);
        float swing = (float) Math.sin(limbSwing * 0.6662f) * 0.35f * limbSwingAmount;
        pose.m_252781_(new Quaternionf().rotationXYZ(swing, 0, swing * 0.4f));
        pose.m_85841_(SCALE, -SCALE, -SCALE);                               // model space is upside down
        pose.m_252880_(-0.5f, -1f, -0.5f);                                  // block's top centre at the hook
        Minecraft.m_91087_().m_91289_().m_110912_(state, pose, buffers, light, OverlayTexture.f_118083_);
        pose.m_85849_();
    }
}
