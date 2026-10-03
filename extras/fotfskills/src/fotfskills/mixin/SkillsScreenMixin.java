package fotfskills.mixin;

import fotfskills.SkillStacks;
import fotfskills.SkillTooltips;
import java.util.List;
import net.minecraft.util.FormattedCharSequence;
import net.puffish.skillsmod.client.config.ClientCategoryConfig;
import java.util.Optional;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;
import net.puffish.skillsmod.api.Skill;
import net.puffish.skillsmod.client.config.skill.ClientSkillConfig;
import net.puffish.skillsmod.client.config.skill.ClientSkillDefinitionConfig;
import net.puffish.skillsmod.client.data.ClientCategoryData;
import net.puffish.skillsmod.client.gui.SkillsScreen;
import org.joml.Vector2i;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.ModifyVariable;
import org.spongepowered.asm.mixin.injection.Redirect;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * Pufferfish's skill screen, made compact and rank-aware:
 * - Window: the screen lays itself out over its own width/height (f_96543_/f_96544_). init (m_7856_) shrinks those
 *   to an advancement-like window and remembers the offset that centres it; render (m_88315_) dims the whole game
 *   window, then draws the screen translated by that offset; mouse handlers and the content scissor get the same
 *   offset so clicks, dragging, scrolling and clipping line up.
 * - Ranks: only one rank of a stacked node is drawn and clickable (SkillStacks), and every stack shows owned/total.
 * - Tiers: nodes in tiers the player hasn't reached are drawn grey; open tiers' numeral tiles light up.
 * - Tooltips: owned effect in white, next rank in grey (SkillTooltips).
 */
@Mixin(value = SkillsScreen.class, remap = false)
public abstract class SkillsScreenMixin extends Screen {
    @Shadow(remap = false)
    private Optional<ClientCategoryData> optActiveCategoryData;

    @Unique
    private int fotfskills$offsetX;
    @Unique
    private int fotfskills$offsetY;
    @Unique
    private int fotfskills$realWidth;
    @Unique
    private int fotfskills$realHeight;

    protected SkillsScreenMixin(Component title) {
        super(title);
    }

    // ---- compact window ----

    @Inject(method = "m_7856_", at = @At("HEAD"), remap = false)
    private void fotfskills$shrinkWindow(CallbackInfo ci) {
        fotfskills$realWidth = this.f_96543_;
        fotfskills$realHeight = this.f_96544_;
        int width = Math.min(fotfskills$realWidth, SkillStacks.WINDOW_WIDTH);
        int height = Math.min(fotfskills$realHeight, SkillStacks.WINDOW_HEIGHT);
        fotfskills$offsetX = (fotfskills$realWidth - width) / 2;
        fotfskills$offsetY = (fotfskills$realHeight - height) / 2;
        this.f_96543_ = width;
        this.f_96544_ = height;
    }

    @Inject(method = "m_88315_", at = @At("HEAD"), remap = false)
    private void fotfskills$beginWindow(GuiGraphics graphics, int mouseX, int mouseY, float partialTick, CallbackInfo ci) {
        graphics.m_280509_(0, 0, fotfskills$realWidth, fotfskills$realHeight, 0xC0101010);
        graphics.m_280168_().m_85836_();
        graphics.m_280168_().m_252880_(fotfskills$offsetX, fotfskills$offsetY, 0);
    }

    @Inject(method = "m_88315_", at = @At("TAIL"), remap = false)
    private void fotfskills$endWindow(GuiGraphics graphics, int mouseX, int mouseY, float partialTick, CallbackInfo ci) {
        graphics.m_280168_().m_85849_();
    }

    /** The dimmed full-window background is drawn in beginWindow instead (renderBackground only covers the window). */
    @Redirect(method = "m_88315_", remap = false,
            at = @At(value = "INVOKE", target = "Lnet/puffish/skillsmod/client/gui/SkillsScreen;m_280273_(Lnet/minecraft/client/gui/GuiGraphics;)V", remap = false))
    private void fotfskills$skipBackground(SkillsScreen screen, GuiGraphics graphics) {
    }

    @ModifyVariable(method = "m_88315_", at = @At("HEAD"), ordinal = 0, argsOnly = true, remap = false)
    private int fotfskills$renderMouseX(int x) {
        return x - fotfskills$offsetX;
    }

    @ModifyVariable(method = "m_88315_", at = @At("HEAD"), ordinal = 1, argsOnly = true, remap = false)
    private int fotfskills$renderMouseY(int y) {
        return y - fotfskills$offsetY;
    }

    @Redirect(method = "drawContent", remap = false,
            at = @At(value = "INVOKE", target = "Lnet/minecraft/client/gui/GuiGraphics;m_280588_(IIII)V", remap = false))
    private void fotfskills$offsetScissor(GuiGraphics graphics, int x1, int y1, int x2, int y2) {
        graphics.m_280588_(x1 + fotfskills$offsetX, y1 + fotfskills$offsetY, x2 + fotfskills$offsetX, y2 + fotfskills$offsetY);
    }

    @ModifyVariable(method = {"m_6375_", "m_6348_", "m_7979_", "m_6050_"}, at = @At("HEAD"), ordinal = 0, argsOnly = true, remap = false)
    private double fotfskills$mouseX(double x) {
        return x - fotfskills$offsetX;
    }

    @ModifyVariable(method = {"m_6375_", "m_6348_", "m_7979_", "m_6050_"}, at = @At("HEAD"), ordinal = 1, argsOnly = true, remap = false)
    private double fotfskills$mouseY(double y) {
        return y - fotfskills$offsetY;
    }

    // ---- one tile per node ----

    @Inject(method = "lambda$drawContentWithCategory$22", at = @At("HEAD"), cancellable = true, remap = false)
    private void fotfskills$drawShownRankOnly(GuiGraphics graphics, @org.spongepowered.asm.mixin.injection.Coerce Object textures,
                                              ClientSkillConfig skill, ClientCategoryData data, @org.spongepowered.asm.mixin.injection.Coerce Object items,
                                              ClientSkillDefinitionConfig definition, CallbackInfo ci) {
        if (!SkillStacks.isShown(data, skill)) {
            ci.cancel();
        }
    }

    /** Grey out tiers the player hasn't reached; light up open tiers' numeral tiles (SkillStacks.displayState). */
    @Redirect(method = "lambda$drawContentWithCategory$22", remap = false,
            at = @At(value = "INVOKE", target = "Lnet/puffish/skillsmod/client/data/ClientCategoryData;getSkillState(Lnet/puffish/skillsmod/client/config/skill/ClientSkillConfig;)Lnet/puffish/skillsmod/api/Skill$State;", remap = false))
    private Skill.State fotfskills$tierState(ClientCategoryData data, ClientSkillConfig skill) {
        return SkillStacks.displayState(data, skill, data.getSkillState(skill));
    }

    @Inject(method = "isInsideSkill", at = @At("HEAD"), cancellable = true, remap = false)
    private void fotfskills$clickShownRankOnly(Vector2i mouse, ClientSkillConfig skill, ClientSkillDefinitionConfig definition,
                                               CallbackInfoReturnable<Boolean> cir) {
        optActiveCategoryData.ifPresent(data -> {
            if (!SkillStacks.isShown(data, skill)) {
                cir.setReturnValue(false);
            }
        });
    }

    @Unique
    private ClientCategoryData fotfskills$tooltipData;
    @Unique
    private ClientSkillConfig fotfskills$tooltipSkill;

    /** Remembers which skill the hover tooltip is for (lambda$drawContentWithCategory$21 builds it). */
    @Inject(method = "lambda$drawContentWithCategory$21", at = @At("HEAD"), remap = false)
    private void fotfskills$rememberTooltipSkill(ClientCategoryConfig config, ClientCategoryData data,
                                                 @org.spongepowered.asm.mixin.injection.Coerce Object connections,
                                                 GuiGraphics graphics, ClientSkillConfig skill, CallbackInfo ci) {
        fotfskills$tooltipData = data;
        fotfskills$tooltipSkill = skill;
    }

    /** Current effect in white, next rank in grey (SkillTooltips); tier/OR tiles keep the original tooltip. */
    @Redirect(method = "lambda$drawContentWithCategory$21", remap = false,
            at = @At(value = "INVOKE", target = "Lnet/puffish/skillsmod/client/gui/SkillsScreen;m_257959_(Ljava/util/List;)V", remap = false))
    private void fotfskills$rankTooltip(SkillsScreen screen, List<FormattedCharSequence> original) {
        List<FormattedCharSequence> lines = fotfskills$tooltipData == null ? null
                : SkillTooltips.build(this.f_96541_, fotfskills$tooltipData, fotfskills$tooltipSkill);
        this.m_257959_(lines != null ? lines : original);
    }

    /** Draws owned/total on every rank stack, inside the tree's transform (just before it is popped). */
    @Inject(method = "drawContentWithCategory", remap = false,
            at = @At(value = "INVOKE", target = "Lcom/mojang/blaze3d/vertex/PoseStack;m_85849_()V", remap = false))
    private void fotfskills$drawRankCounters(GuiGraphics graphics, double mouseX, double mouseY, ClientCategoryData data, CallbackInfo ci) {
        graphics.m_280168_().m_85836_();
        graphics.m_280168_().m_252880_(0, 0, 200);   // above item icons, below tooltips (z 400)
        for (ClientSkillConfig skill : data.getConfig().skills().values()) {
            int[] c = SkillStacks.counter(data, skill);
            if (c == null || !SkillStacks.isShown(data, skill)) {
                continue;
            }
            String text = c[0] + "/" + c[1];
            int color = c[0] == c[1] ? 0xFFE3B341 : 0xFFFFFFFF;
            int width = this.f_96547_.m_92895_(text);
            graphics.m_280614_(this.f_96547_, Component.m_237113_(text), skill.x() + 13 - width, skill.y() + 5, color, true);
        }
        graphics.m_280168_().m_85849_();
    }
}
