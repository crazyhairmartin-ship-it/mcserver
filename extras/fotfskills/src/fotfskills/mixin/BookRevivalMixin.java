package fotfskills.mixin;

import java.util.Set;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.entity.LivingEntity;
import net.minecraftforge.event.entity.living.LivingDeathEvent;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.ModifyVariable;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * Book of Familiars revives a dead pet from the copy it saved when the pet was last summoned, taking only the saddle,
 * armour, hand and chest items from the moment of death. Everything else the pet gained since (a collar or collar
 * enchantments, horse armour, a llama carpet, a donkey's chest, levels, a new name) went back to the summon-time copy.
 * The copy is now overlaid with the pet as it was at death, minus the state of dying itself (health, position, effects).
 * The book cancels the death drops, so nothing comes back twice. Pseudo: skipped without the book.
 */
@Pseudo
@Mixin(targets = "net.fayebeard.bookffamiliars.events.ModEvents", remap = false)
public abstract class BookRevivalMixin {
    private static final Set<String> DYING = Set.of("Pos", "Motion", "Rotation", "FallDistance", "Fire", "Air", "OnGround",
            "PortalCooldown", "Health", "HurtTime", "HurtByTimestamp", "DeathTime", "AbsorptionAmount", "ActiveEffects",
            "Brain", "Leash", "Passengers", "FallFlying", "SleepingX", "SleepingY", "SleepingZ", "AngerTime", "AngryAt");
    private static LivingEntity fotfskills$dying;

    @Inject(method = "onFamiliarDeath", at = @At("HEAD"), remap = false)
    private static void fotfskills$remember(LivingDeathEvent event, CallbackInfo ci) {
        fotfskills$dying = event.getEntity();
    }

    /** Local 10: the summon-time copy the pet is revived from (bookoffamiliars 2.2.1). */
    @ModifyVariable(method = "onFamiliarDeath", at = @At("STORE"), index = 10, remap = false)
    private static CompoundTag fotfskills$asAtDeath(CompoundTag revived) {
        LivingEntity pet = fotfskills$dying;
        fotfskills$dying = null;
        if (pet == null || revived == null) {
            return revived;
        }
        CompoundTag atDeath = new CompoundTag();
        pet.m_20223_(atDeath);
        for (String key : atDeath.m_128431_()) {
            if (!DYING.contains(key)) {
                revived.m_128365_(key, atDeath.m_128423_(key).m_6426_());
            }
        }
        return revived;
    }
}
