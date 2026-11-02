package fotfskills.mixin;

import net.minecraft.core.BlockPos;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.ServerLevelAccessor;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Redirect;

/**
 * Fay's Fairies' spawn rule (each fairy's lambda$init$0) asks Monster.isDarkEnoughToSpawn, left over from registering
 * them as monsters. FairyCategoryMixin made them creatures, so they're only tried in animal spawning, where that
 * darkness check almost never passes: nobody had seen one, even in the Twilight Forest (Dylan, 2026-11-02). The check
 * answers yes for fairies; the rest of their rule (not on peaceful, a valid spot) stays, and where they spawn is still
 * set by the fotf fairy biome modifiers. Patched inside their rule because registering a second rule for the same
 * mob crashes the server ("Duplicate registration").
 */
@Pseudo
@Mixin(targets = {"net.mcreator.faysfairies.entity.PinkFairyEntity", "net.mcreator.faysfairies.entity.BlueFairyEntity",
        "net.mcreator.faysfairies.entity.GoldFairyEntity"}, remap = false)
public abstract class FairySpawnLightMixin {
    @Redirect(method = "lambda$init$0", remap = false, require = 0, at = @At(value = "INVOKE", remap = false,
            target = "Lnet/minecraft/world/entity/monster/Monster;m_219009_(Lnet/minecraft/world/level/ServerLevelAccessor;Lnet/minecraft/core/BlockPos;Lnet/minecraft/util/RandomSource;)Z"))
    private static boolean fotfskills$anyLight(ServerLevelAccessor level, BlockPos pos, RandomSource random) {
        return true;
    }
}
