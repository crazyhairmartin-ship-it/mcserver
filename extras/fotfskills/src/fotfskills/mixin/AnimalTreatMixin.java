package fotfskills.mixin;

import fotfskills.perk.Perks;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.animal.Animal;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * Treat Saver: Animal.usePlayerItem (m_142075_) is where feeding, breeding and taming food is used up; on a
 * successful roll the stack is topped up by one first, so vanilla's shrink(1) leaves it unchanged.
 */
@Mixin(value = Animal.class, remap = false)
public abstract class AnimalTreatMixin {
    @Inject(method = "m_142075_", at = @At("HEAD"), remap = false)
    private void fotfskills$saveTreat(Player player, InteractionHand hand, ItemStack stack, CallbackInfo ci) {
        if (player instanceof ServerPlayer server && !server.m_7500_() && !stack.m_41619_() && Perks.roll(server, "treat_saver")) {
            stack.m_41769_(1);
        }
    }
}
