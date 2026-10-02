package fotfmail;

import com.github.alexthe668.domesticationinnovation.server.enchantment.DIEnchantmentRegistry;
import com.github.alexthe668.domesticationinnovation.server.entity.TameableUtils;
import java.util.Map;
import java.util.WeakHashMap;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.enchantment.Enchantment;

/**
 * Client side: Domestication Innovation draws Shadow Hands and Blazing Protection bars around a pet all the time.
 * These only show while the pet is fighting (has an attack target) or was just hurt, and linger LINGER_TICKS after.
 * Used by mixin/LayerPetOverlaysMixin; every other collar effect is already only drawn while it's in use.
 */
public final class CollarEffectTiming {
    private static final int LINGER_TICKS = 100; // 5 seconds
    private static final Map<LivingEntity, Integer> LAST_ACTIVE = new WeakHashMap<>();

    private CollarEffectTiming() {
    }

    public static boolean isHiddenWhenIdle(Enchantment enchantment) {
        return enchantment == DIEnchantmentRegistry.SHADOW_HANDS || enchantment == DIEnchantmentRegistry.BLAZING_PROTECTION;
    }

    /** Whether a pet's idle-hidden effects should show this frame. */
    public static boolean isActive(LivingEntity pet) {
        int now = pet.f_19797_;
        boolean active = pet.f_20916_ > 0 || TameableUtils.getPetAttackTarget(pet) != null;
        if (active) {
            LAST_ACTIVE.put(pet, now);
            return true;
        }
        Integer last = LAST_ACTIVE.get(pet);
        return last != null && now - last >= 0 && now - last < LINGER_TICKS;
    }
}
