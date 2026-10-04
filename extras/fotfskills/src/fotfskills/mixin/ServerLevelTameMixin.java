package fotfskills.mixin;

import fotfskills.perk.PetPerks;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.TamableAnimal;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** Gentle Hand: a wild tamable animal broadcasting entity event 6 (failed-tame smoke, ServerLevel.broadcastEntityEvent = m_7605_). */
@Mixin(value = ServerLevel.class, remap = false)
public abstract class ServerLevelTameMixin {
    @Inject(method = "m_7605_", at = @At("HEAD"), remap = false)
    private void fotfskills$failedTame(Entity entity, byte event, CallbackInfo ci) {
        if (event == 6 && entity instanceof TamableAnimal animal && !animal.m_21824_()) {
            PetPerks.failedTame(animal);
        }
    }
}
