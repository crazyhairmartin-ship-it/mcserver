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
 * Taming XP for horses tamed without Forge's AnimalTameEvent (tameWithName = m_30637_). Vanilla's riding tame
 * fires the event first (RunAroundLikeCrazyGoal), so those are skipped here; mods that call tameWithName directly are paid.
 */
@Mixin(value = AbstractHorse.class, remap = false)
public abstract class AbstractHorseTameMixin {
    @Inject(method = "m_30637_", at = @At("RETURN"), remap = false)
    private void fotfskills$tameXp(Player player, CallbackInfoReturnable<Boolean> cir) {
        if (cir.getReturnValueZ() && player instanceof ServerPlayer server
                && !fotfskills.xp.ForgeXpEvents.TAMED_BY_EVENT.remove((AbstractHorse) (Object) this)) {
            AmountSource.award(server, "tame", 1);
        }
    }
}
