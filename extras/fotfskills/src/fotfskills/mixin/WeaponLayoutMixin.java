package fotfskills.mixin;

import fotfskills.client.WeaponLayout;
import fotfskills.client.WeaponLayoutHooks;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.Redirect;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * Weapon Master draws the local player's hotbar weapons by slot; this hands it the hotbar rearranged by weapon type
 * (client/WeaponLayout), and moves "the selected slot" with its item so the held weapon is still the one left out.
 */
@Mixin(targets = "com.minecraftserverzone.weaponmaster.itemlayers.HumanoidItemLayer", remap = false)
public abstract class WeaponLayoutMixin {
    @Inject(method = "renderWithItems", remap = false, require = 0, at = @At("HEAD"))
    private void fotfskills$arrange(LivingEntity entity, com.mojang.blaze3d.vertex.PoseStack pose,
                                    net.minecraft.client.renderer.MultiBufferSource buffers, int light, CallbackInfo ci) {
        WeaponLayoutHooks.current = null;
        if (entity instanceof Player player) {
            ItemStack[] hotbar = new ItemStack[9];
            for (int i = 0; i < 9; i++) {
                hotbar[i] = player.m_150109_().m_8020_(i);
            }
            WeaponLayoutHooks.current = WeaponLayoutHooks.arrange(WeaponLayoutHooks.localAttachments(), hotbar);
        }
    }

    @Redirect(method = "renderWithItems", remap = false, require = 0, at = @At(value = "INVOKE",
            target = "Lnet/minecraft/world/entity/player/Inventory;m_8020_(I)Lnet/minecraft/world/item/ItemStack;"))
    private ItemStack fotfskills$item(Inventory inventory, int slot) {
        int[] shown = WeaponLayoutHooks.current;
        return inventory.m_8020_(shown != null && slot >= 0 && slot < 9 ? shown[slot] : slot);
    }

    @Redirect(method = "renderWithItems", remap = false, require = 0, at = @At(value = "FIELD",
            target = "Lnet/minecraft/world/entity/player/Inventory;f_35977_:I", opcode = org.objectweb.asm.Opcodes.GETFIELD))
    private int fotfskills$selected(Inventory inventory) {
        int[] shown = WeaponLayoutHooks.current;
        int selected = inventory.f_35977_;
        return shown != null && selected >= 0 && selected < 9 ? WeaponLayout.displayOf(shown, selected) : selected;
    }
}
