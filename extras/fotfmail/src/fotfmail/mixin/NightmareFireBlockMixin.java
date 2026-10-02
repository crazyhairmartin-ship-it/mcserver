package fotfmail.mixin;

import com.hackshop.ultimate_unicorn.blocks.NightmareFireBlock;
import net.minecraft.util.RandomSource;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * The fire Nightmares (Ultimate Unicorn Mod) leave where they step burns out about 5x sooner. Fire ages one step per
 * tick and dies when old; the mod ticks it every 30-39 game ticks (getFireTickDelay = m_221148_), this makes it 6-9.
 */
@Mixin(NightmareFireBlock.class)
public abstract class NightmareFireBlockMixin {
    @Inject(method = "m_221148_", at = @At("HEAD"), cancellable = true, remap = false)
    private static void fotfmail$burnOutSooner(RandomSource random, CallbackInfoReturnable<Integer> cir) {
        cir.setReturnValue(6 + random.m_188503_(4));
    }
}
