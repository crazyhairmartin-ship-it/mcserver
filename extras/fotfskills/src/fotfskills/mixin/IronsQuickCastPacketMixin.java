package fotfskills.mixin;

import fotfskills.compat.ThirdPerson;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** Quick-casting a spell (the client builds this packet): face the third-person crosshair first. See ThirdPerson. */
@Pseudo
@Mixin(targets = "io.redspace.ironsspellbooks.network.casting.QuickCastPacket", remap = false)
public abstract class IronsQuickCastPacketMixin {
    @Inject(method = "<init>(I)V", at = @At("RETURN"), remap = false)
    private void fotfskills$faceCrosshair(int slot, CallbackInfo ci) {
        ThirdPerson.faceCrosshair();
    }
}
