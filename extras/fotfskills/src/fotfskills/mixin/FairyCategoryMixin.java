package fotfskills.mixin;

import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobCategory;
import net.minecraftforge.registries.ForgeRegistries;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * Fay's Fairies registers its friendly, tameable fairies as monsters: they'd never spawn on peaceful and, since they
 * never despawn, would fill the monster cap. They count as creatures (like wolves) instead, so they spawn in sensible
 * numbers from the fotf fairy biome modifiers (kubejs/data/fotf/forge/biome_modifier/fairies_*.json).
 */
@Mixin(value = EntityType.class, remap = false)
public abstract class FairyCategoryMixin {
    @Unique
    private Boolean fotfskills$fairy;

    @Inject(method = "m_20674_", at = @At("HEAD"), cancellable = true, remap = false)
    private void fotfskills$fairiesAreCreatures(CallbackInfoReturnable<MobCategory> cir) {
        if (fotfskills$fairy == null) {
            ResourceLocation id = ForgeRegistries.ENTITY_TYPES.getKey((EntityType<?>) (Object) this);
            if (id == null) {
                return;                                    // not registered yet: decide on a later call
            }
            fotfskills$fairy = id.m_135827_().equals("fays_fairies");
        }
        if (fotfskills$fairy) {
            cir.setReturnValue(MobCategory.CREATURE);
        }
    }
}
