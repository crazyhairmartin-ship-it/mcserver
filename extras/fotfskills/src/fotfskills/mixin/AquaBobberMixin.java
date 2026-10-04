package fotfskills.mixin;

import fotfskills.perk.BiteTime;
import fotfskills.perk.Perks;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.projectile.FishingHook;
import net.minecraft.world.item.ItemStack;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.Redirect;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * Aquaculture's bobber has its own catchingFish (m_37145_), so FishingHookMixin never reaches it. Same wait formula and
 * write order as vanilla: after the Lure subtraction (4th write, ordinal 3) the wait is shortened by Patient Angler,
 * Storm Fisher and, while the rod carries bait, Lure Master. Bait Saver: retrieve (m_37156_) damages the bait with one
 * hurt call; skipping it keeps the bait.
 */
@Pseudo
@Mixin(targets = "com.teammetallurgy.aquaculture.entity.AquaFishingBobberEntity", remap = false)
public abstract class AquaBobberMixin {
    @Shadow(remap = false)
    private ItemStack fishingRod;

    @Inject(method = "m_37145_", remap = false, require = 0, at = @At(value = "FIELD", opcode = 181 /* PUTFIELD */,
            target = "Lcom/teammetallurgy/aquaculture/entity/AquaFishingBobberEntity;f_37090_:I", ordinal = 3,
            shift = At.Shift.AFTER, remap = false))
    private void fotfskills$shorterWait(CallbackInfo ci) {
        FishingHook hook = (FishingHook) (Object) this;
        if (!(hook.m_37168_() instanceof ServerPlayer player)) {
            return;
        }
        double faster = Perks.get(player, "bite_speed");
        if (hook.m_9236_().m_46758_(hook.m_20183_().m_7494_())) {
            faster += Perks.get(player, "rain_bite_speed");
        }
        if (fotfskills$hasBait()) {
            faster += Perks.get(player, "lure_master");
        }
        FishingHookAccessor wait = (FishingHookAccessor) hook;
        wait.fotfskills$setTimeUntilLured(BiteTime.scale(wait.fotfskills$getTimeUntilLured(), faster));
    }

    @Redirect(method = "m_37156_", remap = false, require = 0, at = @At(value = "INVOKE", remap = false,
            target = "Lnet/minecraft/world/item/ItemStack;m_220157_(ILnet/minecraft/util/RandomSource;Lnet/minecraft/server/level/ServerPlayer;)Z"))
    private boolean fotfskills$baitSaver(ItemStack bait, int amount, RandomSource random, ServerPlayer nobody) {
        if (((FishingHook) (Object) this).m_37168_() instanceof ServerPlayer player && Perks.roll(player, "bait_saver")) {
            return false;
        }
        return bait.m_220157_(amount, random, nobody);
    }

    private boolean fotfskills$hasBait() {
        return fishingRod != null && !fishingRod.m_41619_()
                && !com.teammetallurgy.aquaculture.item.AquaFishingRodItem.getHandler(fishingRod).getStackInSlot(1).m_41619_();
    }
}
