package fotfskills.mixin;

import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.world.item.ItemStack;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Invoker;

/** AbstractArrow.getPickupItem (m_7941_) is protected; Quiver Care needs the item to refund. */
@Mixin(value = AbstractArrow.class, remap = false)
public interface AbstractArrowAccessor {
    @Invoker(value = "m_7941_", remap = false)
    ItemStack fotfskills$pickupItem();
}
