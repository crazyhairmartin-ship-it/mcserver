package fotfskills.mixin;

import net.fayebeard.bookffamiliars.network.DeleteTrackedFamiliarPacket;
import net.minecraft.world.entity.Entity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Redirect;

/**
 * Book of Familiars' Delete becomes Unbind for a familiar out in the world: the book forgets it, the creature stays.
 * The book shows a familiar's label even without a custom name (just its type, e.g. "Pegasus"); unbinding hides it.
 */
@Mixin(value = DeleteTrackedFamiliarPacket.class, remap = false)
public abstract class FamiliarUnbindTrackedMixin {
    @Redirect(method = "lambda$handle$2", remap = false, at = @At(value = "INVOKE",
            target = "Lnet/minecraft/world/entity/Entity;m_146870_()V"))
    private static void fotfskills$keep(Entity familiar) {
        if (!familiar.m_8077_()) familiar.m_20340_(false);
    }
}
