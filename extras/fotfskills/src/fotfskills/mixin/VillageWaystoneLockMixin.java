package fotfskills.mixin;

import net.blay09.mods.waystones.api.IWaystone;
import net.blay09.mods.waystones.api.WaystoneOrigin;
import net.blay09.mods.waystones.core.WaystoneEditPermissions;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * Village waystones keep their names (given by compat/VillageWaystones): only creative players can edit them.
 * Players' own waystones and wild ones stay editable as usual (Waystones' restrictRenameToOwner stays off).
 */
@Mixin(targets = "net.blay09.mods.waystones.core.PlayerWaystoneManager", remap = false)
public abstract class VillageWaystoneLockMixin {
    @Inject(method = "mayEditWaystone", remap = false, at = @At("HEAD"), cancellable = true)
    private static void fotfskills$villageLocked(Player player, Level level, IWaystone waystone,
                                                 CallbackInfoReturnable<WaystoneEditPermissions> cir) {
        if (waystone != null && waystone.getOrigin() == WaystoneOrigin.VILLAGE && !player.m_150110_().f_35937_) {
            cir.setReturnValue(WaystoneEditPermissions.NOT_CREATIVE);
        }
    }
}
