package fotfskills.mixin;

import fotfskills.compat.ThirdPerson;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** Casting from the spellbook (the client builds this packet): face the third-person crosshair first. See ThirdPerson. */
@Pseudo
@Mixin(targets = "io.redspace.ironsspellbooks.network.casting.CastPacket", remap = false)
public abstract class IronsCastPacketMixin {
    @Inject(method = "<init>()V", at = @At("RETURN"), remap = false)
    private void fotfskills$faceCrosshair(CallbackInfo ci) {
        ThirdPerson.faceCrosshair();
    }
}
