package fotfmail.mixin;

import com.github.alexthe668.domesticationinnovation.client.render.LayerPetOverlays;
import com.github.alexthe668.domesticationinnovation.server.entity.TameableUtils;
import fotfmail.CollarEffectTiming;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.enchantment.Enchantment;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Redirect;

/**
 * Shadow Hands and Blazing Protection bars only draw while the pet is fighting or was just hurt (plus a few seconds),
 * instead of all the time. The render method (m_6494_) asks TameableUtils whether the pet has each enchantment;
 * for those two, answer "no" while the pet is idle. Gameplay is untouched: this only affects drawing.
 */
@Mixin(LayerPetOverlays.class)
public abstract class LayerPetOverlaysMixin {
    @Redirect(method = "m_6494_", remap = false, require = 0, at = @At(value = "INVOKE", remap = false,
            target = "Lcom/github/alexthe668/domesticationinnovation/server/entity/TameableUtils;hasEnchant(Lnet/minecraft/world/entity/LivingEntity;Lnet/minecraft/world/item/enchantment/Enchantment;)Z"))
    private boolean fotfmail$hasEnchantWhenActive(LivingEntity pet, Enchantment enchantment) {
        if (CollarEffectTiming.isHiddenWhenIdle(enchantment) && !CollarEffectTiming.isActive(pet)) {
            return false;
        }
        return TameableUtils.hasEnchant(pet, enchantment);
    }

    @Redirect(method = "m_6494_", remap = false, require = 0, at = @At(value = "INVOKE", remap = false,
            target = "Lcom/github/alexthe668/domesticationinnovation/server/entity/TameableUtils;getEnchantLevel(Lnet/minecraft/world/entity/LivingEntity;Lnet/minecraft/world/item/enchantment/Enchantment;)I"))
    private int fotfmail$enchantLevelWhenActive(LivingEntity pet, Enchantment enchantment) {
        if (CollarEffectTiming.isHiddenWhenIdle(enchantment) && !CollarEffectTiming.isActive(pet)) {
            return 0;
        }
        return TameableUtils.getEnchantLevel(pet, enchantment);
    }
}
