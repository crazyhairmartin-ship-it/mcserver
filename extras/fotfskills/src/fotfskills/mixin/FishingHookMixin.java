package fotfskills.mixin;

import fotfskills.perk.Perks;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.projectile.FishingHook;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.ModifyArg;

/**
 * Patient Angler / Storm Fisher: shorter wait for a bite. catchingFish (m_37145_) rolls the wait with
 * Mth.nextInt(random, 100, 600) (third nextInt call, ordinal 2); both bounds are scaled down.
 */
@Mixin(value = FishingHook.class, remap = false)
public abstract class FishingHookMixin {
    @ModifyArg(method = "m_37145_", remap = false, index = 1, at = @At(value = "INVOKE",
            target = "Lnet/minecraft/util/Mth;m_216271_(Lnet/minecraft/util/RandomSource;II)I", ordinal = 2, remap = false))
    private int fotfskills$minWait(int min) {
        return scaled(min);
    }

    @ModifyArg(method = "m_37145_", remap = false, index = 2, at = @At(value = "INVOKE",
            target = "Lnet/minecraft/util/Mth;m_216271_(Lnet/minecraft/util/RandomSource;II)I", ordinal = 2, remap = false))
    private int fotfskills$maxWait(int max) {
        return scaled(max);
    }

    private int scaled(int ticks) {
        FishingHook hook = (FishingHook) (Object) this;
        if (!(hook.m_37168_() instanceof ServerPlayer player)) {
            return ticks;
        }
        double faster = Perks.get(player, "bite_speed");
        BlockPos pos = hook.m_20183_();
        if (hook.m_9236_().m_46758_(pos.m_7494_())) {
            faster += Perks.get(player, "rain_bite_speed");
        }
        return Math.max(1, (int) Math.round(ticks * (1 - Math.min(faster, 0.8))));
    }
}
