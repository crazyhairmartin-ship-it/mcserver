package fotfskills.mixin;

import fotfskills.mana.ManaMerge;
import fotfskills.perk.IronsMana;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.LivingEntity;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * Shared mana: on the server, a player's Ars Nouveau mana capability reads and writes Iron's Spells mana (current, set,
 * max). Ars's add/remove go through these, so every Ars spend and refill uses the one pool (Ars's own computed max
 * is recorded in ArsManaRegenMixin). Mobs and the client copy keep Ars's own behaviour.
 */
@Pseudo
@Mixin(targets = "com.hollingsworth.arsnouveau.common.capability.ManaCap", remap = false)
public abstract class ArsManaCapMixin {
    @Shadow(remap = false)
    @Final
    private LivingEntity livingEntity;

    private ServerPlayer fotfskills$player() {
        return ManaMerge.active() && livingEntity instanceof ServerPlayer player ? player : null;
    }

    @Inject(method = "getCurrentMana", at = @At("HEAD"), cancellable = true, remap = false)
    private void fotfskills$current(CallbackInfoReturnable<Double> cir) {
        ServerPlayer player = fotfskills$player();
        if (player != null) {
            cir.setReturnValue(IronsMana.get(player));
        }
    }

    @Inject(method = "setMana", at = @At("HEAD"), cancellable = true, remap = false)
    private void fotfskills$set(double mana, CallbackInfoReturnable<Double> cir) {
        ServerPlayer player = fotfskills$player();
        if (player != null) {
            double current = IronsMana.get(player);
            // Ars calls addMana(0) every few ticks (its regen is off): a no-change write must not clamp the pool
            cir.setReturnValue(Math.abs(mana - current) < 1e-6 ? current : IronsMana.set(player, mana));
        }
    }

    @Inject(method = "getMaxMana", at = @At("HEAD"), cancellable = true, remap = false)
    private void fotfskills$max(CallbackInfoReturnable<Integer> cir) {
        ServerPlayer player = fotfskills$player();
        if (player != null) {
            cir.setReturnValue((int) IronsMana.max(player));
        }
    }

}
