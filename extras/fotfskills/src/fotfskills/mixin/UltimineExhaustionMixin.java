package fotfskills.mixin;

import fotfskills.perk.Perks;
import fotfskills.perk.Tunnel;
import net.minecraft.server.level.ServerPlayer;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Redirect;

/** Tunnel Vision: FTB Ultimine's hunger cost (one causeFoodExhaustion call in blockBroken) shrinks per rank. */
@Pseudo
@Mixin(targets = "dev.ftb.mods.ftbultimine.FTBUltimine", remap = false)
public abstract class UltimineExhaustionMixin {
    @Redirect(method = "blockBroken", remap = false, require = 0,
            at = @At(value = "INVOKE", target = "Lnet/minecraft/server/level/ServerPlayer;m_36399_(F)V", remap = false))
    private void fotfskills$lessHunger(ServerPlayer player, float exhaustion) {
        player.m_36399_(Tunnel.scale(exhaustion, Perks.get(player, "tunnel_vision")));
    }
}
