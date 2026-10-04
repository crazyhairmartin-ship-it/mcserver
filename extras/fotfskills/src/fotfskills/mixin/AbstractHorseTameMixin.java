package fotfskills.mixin;

import fotfskills.xp.AmountSource;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.animal.horse.AbstractHorse;
import net.minecraft.world.entity.player.Player;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * Taming XP for horses: taming a horse by riding it (tameWithName = m_30637_) never fires Forge's AnimalTameEvent, so
 * the tame XP source is paid here. Covers donkeys, mules, llamas and the unicorn mod's horses.
 */
@Mixin(value = AbstractHorse.class, remap = false)
public abstract class AbstractHorseTameMixin {
    @Inject(method = "m_30637_", at = @At("RETURN"), remap = false)
    private void fotfskills$tameXp(Player player, CallbackInfoReturnable<Boolean> cir) {
        if (cir.getReturnValueZ() && player instanceof ServerPlayer server) {
            AmountSource.award(server, "tame", 1);
        }
    }
}
