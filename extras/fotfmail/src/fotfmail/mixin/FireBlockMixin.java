package fotfmail.mixin;

import com.hackshop.ultimate_unicorn.blocks.NightmareFireBlock;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.block.FireBlock;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Redirect;

/**
 * When a Nightmare's hoof fire is placed, its first tick comes after 4-6 game ticks instead of vanilla fire's 30-39,
 * so it can go out quickly (NightmareFireBlockMixin). FireBlock.onPlace (m_6807_) schedules that first tick with
 * getFireTickDelay (m_221148_); every other fire keeps vanilla's delay.
 */
@Mixin(FireBlock.class)
public abstract class FireBlockMixin {
    @Redirect(method = "m_6807_", remap = false, at = @At(value = "INVOKE", remap = false,
            target = "Lnet/minecraft/world/level/block/FireBlock;m_221148_(Lnet/minecraft/util/RandomSource;)I"))
    private int fotfmail$quickFirstTick(RandomSource random) {
        if ((Object) this instanceof NightmareFireBlock) {
            return 4 + random.m_188503_(3);
        }
        return 30 + random.m_188503_(10);
    }
}
