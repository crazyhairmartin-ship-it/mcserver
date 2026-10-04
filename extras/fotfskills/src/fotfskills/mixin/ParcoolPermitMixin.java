package fotfskills.mixin;

import fotfskills.perk.Perks;
import java.util.Map;
import net.minecraft.world.entity.player.Player;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * ParCool moves earned in the Agility tree. ParCool's own skill tree is off (every move allowed); this keeps the athletic
 * moves locked until the player takes the node that unlocks them. permit() runs on client and server, and both have
 * the player's perk totals.
 */
@Pseudo
@Mixin(targets = "com.alrex.parcool.common.Parkourability", remap = false)
public abstract class ParcoolPermitMixin {
    private static final Map<String, String> UNLOCKED_BY = Map.of(
            "wall_run", "pc_freerunner", "horizontal_wall_run", "pc_freerunner", "castaway", "pc_freerunner",
            "wall_jump", "pc_spring", "long_jump", "pc_spring", "charge_jump", "pc_spring",
            "skydive", "pc_skydive", "trick_jump", "pc_trick");

    @Shadow(remap = false)
    @Final
    private Player player;

    @Inject(method = "permit", at = @At("RETURN"), cancellable = true, remap = false, require = 0)
    private void fotfskills$agilityUnlocks(com.alrex.parcool.api.action.ActionEntry<?> action, CallbackInfoReturnable<Boolean> cir) {
        if (!cir.getReturnValueZ() || player == null) {
            return;
        }
        String perk = UNLOCKED_BY.get(action.id().m_135815_());
        if (perk != null && Perks.get(player, perk) <= 0) {
            cir.setReturnValue(false);
        }
    }
}
