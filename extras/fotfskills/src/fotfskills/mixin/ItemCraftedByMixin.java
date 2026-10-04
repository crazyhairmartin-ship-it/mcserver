package fotfskills.mixin;

import fotfskills.perk.CraftPerks;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * Crafted-gear perks on the real crafted stack. Item.onCraftedBy (m_7836_) gets the stack that ends up in the
 * inventory both for a normal take (via ItemStack.onCraftedBy) and for shift-click crafting (the menus call it
 * directly), whereas ItemCraftedEvent only sees a throwaway copy on shift-click.
 */
@Mixin(value = Item.class, remap = false)
public abstract class ItemCraftedByMixin {
    @Inject(method = "m_7836_", at = @At("HEAD"), remap = false)
    private void fotfskills$improveCraftedGear(ItemStack stack, Level level, Player player, CallbackInfo ci) {
        if (!level.f_46443_ && player instanceof ServerPlayer server && CraftPerks.craftingGrid(server.f_36096_)) {
            CraftPerks.improve(server, stack);
        }
    }
}
