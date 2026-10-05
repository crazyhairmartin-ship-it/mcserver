package fotfskills.mixin;

import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Redirect;

/** The Immolator's flame strike charges with an empty other hand too (Cataclysm wants a second Immolator there). */
@Pseudo
@Mixin(targets = "com.github.L_Ender.cataclysm.items.The_Immolator", remap = false)
public abstract class ImmolatorOneHandMixin {
    @Redirect(method = "m_7203_", remap = false, require = 0,
            at = @At(value = "INVOKE", target = "Lnet/minecraft/world/item/ItemStack;m_150930_(Lnet/minecraft/world/item/Item;)Z", remap = false))
    private boolean fotfskills$emptyHandCounts(ItemStack otherHand, Item immolator) {
        return otherHand.m_150930_(immolator) || otherHand.m_41619_();
    }
}
