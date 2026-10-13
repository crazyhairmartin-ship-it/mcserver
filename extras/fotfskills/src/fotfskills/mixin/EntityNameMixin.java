package fotfskills.mixin;

import fotfskills.world.NamedPets;
import net.minecraft.network.chat.Component;
import net.minecraft.world.entity.Entity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** Every rename (name tag, Book of Familiars, commands, loading from disk) goes through setCustomName. See NamedPets. */
@Mixin(value = Entity.class, remap = false)
public abstract class EntityNameMixin {
    @Inject(method = "m_6593_", at = @At("TAIL"), remap = false)
    private void fotfskills$namedPet(Component name, CallbackInfo ci) {
        Entity self = (Entity) (Object) this;
        if (name != null && self.m_9236_() != null && !self.m_9236_().m_5776_()) {
            NamedPets.renamed(self);
        }
    }
}
