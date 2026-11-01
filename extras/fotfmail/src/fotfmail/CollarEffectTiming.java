package fotfmail;

import com.github.alexthe668.domesticationinnovation.server.enchantment.DIEnchantmentRegistry;
import com.github.alexthe668.domesticationinnovation.server.entity.TameableUtils;
import java.lang.reflect.Method;
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

    private static Object iris;           // Oculus' IrisApi, when it's installed
    private static Method shadowPass;     // IrisApi.isRenderingShadowPass()
    private static boolean irisLooked;

    /**
     * With shaders on, Oculus draws the world a second time for its shadow map, and Domestication Innovation's
     * overlays drawn in that pass show up as small stray Shadow Hands fixed on screen in front of everything
     * (Dylan, 2026-11-01). They're skipped in that pass only, so the real ones still show. Oculus is client-only and
     * optional (not on the server or the RP6), so its API is looked up by name.
     */
    public static boolean inShaderShadowPass() {
        if (!irisLooked) {
            irisLooked = true;
            try {
                Class<?> api = Class.forName("net.irisshaders.iris.api.v0.IrisApi");
                iris = api.getMethod("getInstance").invoke(null);
                shadowPass = api.getMethod("isRenderingShadowPass");
            } catch (ReflectiveOperationException | LinkageError e) {
                iris = null;
            }
        }
        if (iris == null) {
            return false;
        }
        try {
            return (Boolean) shadowPass.invoke(iris);
        } catch (ReflectiveOperationException e) {
            return false;
        }
    }

    /** Whether a pet's idle-hidden effects should show this frame. */
    public static boolean isActive(LivingEntity pet) {
        int now = pet.f_19797_;
        // only a real fight counts: a target that's alive, close and not the owner. Domestication Innovation's synced
        // target could be stale (dead, gone, or an old id now pointing at some other entity), which kept the hands
        // showing all the time and drew stray small ones elsewhere on screen (Dylan, 2026-10-25)
        net.minecraft.world.entity.Entity target = TameableUtils.getPetAttackTarget(pet);
        boolean fighting = target != null && target.m_6084_() && target != pet
                && target.m_20280_(pet) < 24 * 24 && target != TameableUtils.getOwnerOf(pet);
        boolean active = pet.f_20916_ > 0 || fighting;
        if (active) {
            LAST_ACTIVE.put(pet, now);
            return true;
        }
        Integer last = LAST_ACTIVE.get(pet);
        return last != null && now - last >= 0 && now - last < LINGER_TICKS;
    }
}
