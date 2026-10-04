package fotfskills.mixin;

import net.minecraftforge.fml.ModList;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/** Shared mana shows on Iron's bar only: Ars Nouveau's mana HUD is hidden while Iron's Spells is installed. */
@Pseudo
@Mixin(targets = "com.hollingsworth.arsnouveau.client.gui.GuiManaHUD", remap = false)
public abstract class ArsManaHudMixin {
    @Inject(method = "shouldDisplayBar", at = @At("HEAD"), cancellable = true, remap = false)
    private static void fotfskills$ironsBarOnly(CallbackInfoReturnable<Boolean> cir) {
        if (ModList.get().isLoaded("irons_spellbooks")) {
            cir.setReturnValue(false);
        }
    }
}
