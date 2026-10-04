package fotfskills.mixin;

import com.hollingsworth.arsnouveau.api.spell.SpellResolver;
import fotfskills.xp.AmountSource;
import net.minecraft.server.level.ServerPlayer;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * Ars Nouveau: Magic XP when a spell actually spends mana. SpellCastEvent also fires for casts that fail (a touch
 * spell aimed at the air), so XP comes from expendMana, which only runs on success, using the discounted cost.
 * Pseudo: skipped quietly if Ars Nouveau is not installed.
 */
@Pseudo
@Mixin(value = SpellResolver.class, remap = false)
public abstract class ArsSpellResolverMixin {
    @Inject(method = "expendMana", at = @At("HEAD"), remap = false)
    private void fotfskills$magicXp(CallbackInfo ci) {
        SpellResolver resolver = (SpellResolver) (Object) this;
        if (resolver.spellContext.getUnwrappedCaster() instanceof ServerPlayer player && !player.m_7500_()) {
            AmountSource.award(player, "cast_spell", resolver.getResolveCost());
        }
    }
}
