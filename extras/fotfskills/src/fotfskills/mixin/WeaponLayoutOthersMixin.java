package fotfskills.mixin;

import com.minecraftserverzone.weaponmaster.setup.playerdata.IPlayerData;
import com.minecraftserverzone.weaponmaster.setup.playerdata.PlayerData;
import fotfskills.client.WeaponLayout;
import fotfskills.client.WeaponLayoutHooks;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.Redirect;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** The same weapon-type arrangement for other players, whose hotbars Weapon Master keeps in its synced PlayerData. */
@Mixin(targets = "com.minecraftserverzone.weaponmaster.itemlayers.RenderHelper", remap = false)
public abstract class WeaponLayoutOthersMixin {
    private static ItemStack[] fotfskills$shown;

    @Inject(method = "renderOtherPlayerWithItems", remap = false, require = 0, at = @At("HEAD"))
    private static void fotfskills$arrange(Player player, com.mojang.blaze3d.vertex.PoseStack pose,
                                           net.minecraft.client.renderer.MultiBufferSource buffers, int light,
                                           net.minecraft.client.model.HumanoidModel<?> model, CallbackInfo ci) {
        PlayerData data = ((IPlayerData) player).getPlayerData();
        WeaponLayoutHooks.current = data == null ? null : WeaponLayoutHooks.arrange(player, data.inventory);
        fotfskills$shown = data == null ? null : WeaponLayoutHooks.shown(data.inventory, WeaponLayoutHooks.current);
    }

    @Redirect(method = "renderOtherPlayerWithItems", remap = false, require = 0, at = @At(value = "FIELD",
            target = "Lcom/minecraftserverzone/weaponmaster/setup/playerdata/PlayerData;inventory:[Lnet/minecraft/world/item/ItemStack;",
            opcode = org.objectweb.asm.Opcodes.GETFIELD))
    private static ItemStack[] fotfskills$inventory(PlayerData data) {
        return fotfskills$shown != null ? fotfskills$shown : data.inventory;
    }

    @Redirect(method = "renderOtherPlayerWithItems", remap = false, require = 0, at = @At(value = "FIELD",
            target = "Lcom/minecraftserverzone/weaponmaster/setup/playerdata/PlayerData;selectedSlot:I",
            opcode = org.objectweb.asm.Opcodes.GETFIELD))
    private static int fotfskills$selected(PlayerData data) {
        int[] shown = WeaponLayoutHooks.current;
        int selected = data.selectedSlot;
        return shown != null && selected >= 0 && selected < 9 ? WeaponLayout.displayOf(shown, selected) : selected;
    }
}
