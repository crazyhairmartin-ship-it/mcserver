package fotfskills.pet;

import com.github.alexthe668.domesticationinnovation.server.entity.TameableUtils;
import net.minecraft.world.entity.LivingEntity;

/** Domestication Innovation respawns a pet with a pet bed itself; loaded only when that mod is present. */
final class DomesticationBeds {
    private DomesticationBeds() {
    }

    static boolean hasBed(LivingEntity pet) {
        return TameableUtils.getPetBedPos(pet) != null;
    }
}
