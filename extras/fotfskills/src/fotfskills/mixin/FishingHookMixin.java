package fotfskills.mixin;

import fotfskills.perk.BiteTime;
import fotfskills.perk.Perks;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.projectile.FishingHook;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * Patient Angler / Storm Fisher: shorter wait for a bite. catchingFish (m_37145_) sets timeUntilLured (f_37090_) to
 * nextInt(100, 600), then subtracts Lure (the 4th write to the field, ordinal 3). The wait is scaled after that, and
 * only while positive (BiteTime), so stacking the perk with Lure III never stops fish biting.
 */
@Mixin(value = FishingHook.class, remap = false)
public abstract class FishingHookMixin {
    @Shadow(remap = false)
    private int f_37090_;

    @Inject(method = "m_37145_", remap = false, at = @At(value = "FIELD", opcode = 181 /* PUTFIELD */,
            target = "Lnet/minecraft/world/entity/projectile/FishingHook;f_37090_:I", ordinal = 3, shift = At.Shift.AFTER, remap = false))
    private void fotfskills$shorterWait(CallbackInfo ci) {
        FishingHook hook = (FishingHook) (Object) this;
        if (!(hook.m_37168_() instanceof ServerPlayer player)) {
            return;
        }
        double faster = Perks.get(player, "bite_speed");
        if (hook.m_9236_().m_46758_(hook.m_20183_().m_7494_())) {
            faster += Perks.get(player, "rain_bite_speed");
        }
        f_37090_ = BiteTime.scale(f_37090_, faster);
    }
}
