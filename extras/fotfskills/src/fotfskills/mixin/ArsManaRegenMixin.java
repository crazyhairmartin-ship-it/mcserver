package fotfskills.mixin;

import fotfskills.mana.ManaMerge;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.player.Player;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * Shared mana has one regen (Iron's). Ars's regen per second for a player is recorded (its part above Ars's base becomes
 * an Iron's regen bonus) and Ars's own regen returns 0. ManaUtil.getManaRegen(Player).
 */
@Pseudo
@Mixin(targets = "com.hollingsworth.arsnouveau.api.util.ManaUtil", remap = false)
public abstract class ArsManaRegenMixin {
    @Inject(method = "getManaRegen", at = @At("RETURN"), cancellable = true, remap = false)
    private static void fotfskills$oneRegen(Player player, CallbackInfoReturnable<Double> cir) {
        if (ManaMerge.active() && player instanceof ServerPlayer server) {
            ManaMerge.recordArsRegen(server.m_20148_(), cir.getReturnValue());
            cir.setReturnValue(0.0);
        }
    }
}
