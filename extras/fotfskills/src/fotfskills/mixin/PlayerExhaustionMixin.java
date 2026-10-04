package fotfskills.mixin;

import fotfskills.perk.Perks;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.player.Player;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.ModifyVariable;

/** Trail Rations: hunger drain while sprinting is reduced. Player.causeFoodExhaustion = m_36399_. */
@Mixin(value = Player.class, remap = false)
public abstract class PlayerExhaustionMixin {
    @ModifyVariable(method = "m_36399_", at = @At("HEAD"), ordinal = 0, argsOnly = true, remap = false)
    private float fotfskills$trailRations(float exhaustion) {
        Player player = (Player) (Object) this;
        if (player instanceof ServerPlayer server && server.m_20142_()) {
            return (float) (exhaustion * (1 - Perks.get(server, "trail_rations")));
        }
        return exhaustion;
    }
}
