package fotfskills.mixin;

import fotfskills.xp.AmountSource;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.food.FoodProperties;
import net.minecraft.world.inventory.CraftingMenu;
import net.minecraft.world.inventory.InventoryMenu;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * Cooking XP for food taken from any station except the crafting grid (so crate/block un-crafting loops give
 * nothing), and Crafting XP for gear (damageable items) from any station. ItemStack.onCraftedBy = m_41678_.
 */
@Mixin(value = ItemStack.class, remap = false)
public abstract class ItemStackCraftedMixin {
    @Inject(method = "m_41678_", at = @At("HEAD"), remap = false)
    private void fotfskills$craftedXp(Level level, Player player, int amount, CallbackInfo ci) {
        if (!(player instanceof ServerPlayer server) || amount <= 0) {
            return;
        }
        ItemStack stack = (ItemStack) (Object) this;
        boolean grid = player.f_36096_ instanceof CraftingMenu || player.f_36096_ instanceof InventoryMenu;
        if (stack.m_41614_() && !grid) {
            FoodProperties food = stack.m_41720_().m_41473_();   // Item.getFoodProperties()
            if (food != null) {
                AmountSource.award(server, "cook", (double) food.m_38744_() * amount);
            }
        } else if (stack.m_41763_()) {
            AmountSource.award(server, "craft_gear", amount);
        }
    }
}
