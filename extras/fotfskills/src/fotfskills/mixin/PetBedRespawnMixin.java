package fotfskills.mixin;

import fotfskills.pet.PetSaveData;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * Domestication Innovation saves a pet that dies with a pet bed and respawns it there the next morning, but its saved
 * data still holds the chest, saddle, armour and lead that already dropped on death (duplicated on respawn). The saved
 * data is stripped of those as the respawn request is created. Pseudo: skipped if DI is not installed.
 */
@Pseudo
@Mixin(targets = "com.github.alexthe668.domesticationinnovation.server.misc.RespawnRequest", remap = false)
public abstract class PetBedRespawnMixin {
    @Inject(method = "<init>", at = @At("RETURN"), remap = false)
    private void fotfskills$noDroppedItems(String entityType, String dimension, CompoundTag entityData, BlockPos bed, long time,
                                           String nametag, CallbackInfo ci) {
        if (entityData != null) {
            PetSaveData.strip(entityData);
        }
    }
}
