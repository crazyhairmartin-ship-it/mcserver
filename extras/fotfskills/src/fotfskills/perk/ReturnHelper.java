package fotfskills.perk;

import java.lang.reflect.Field;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.world.entity.projectile.ThrownTrident;

/**
 * Retriever: sends a thrown weapon back to its thrower with the weapon's own return mechanic, so the catch handles the
 * item (and Spartan's ammo count) and nothing is left on the ground. Tridents get Loyalty I; Spartan Weaponry throwing
 * weapons get their Returning flag. Fields are found by reflection: vanilla's by its SRG name, Spartan's by its own name.
 */
public final class ReturnHelper {
    private static final String SPARTAN = "com.oblivioussp.spartanweaponry.entity.projectile.ThrowingWeaponEntity";
    private static EntityDataAccessor<Byte> loyalty;
    private static EntityDataAccessor<Byte> spartanReturn;
    private static boolean looked;

    private ReturnHelper() {
    }

    /** True if the weapon will now fly back by itself. */
    public static boolean sendBack(AbstractArrow thrown) {
        find();
        EntityDataAccessor<Byte> flag = thrown instanceof ThrownTrident ? loyalty
                : isSpartan(thrown.getClass()) ? spartanReturn : null;
        if (flag == null) {
            return false;
        }
        thrown.m_20088_().m_135381_(flag, (byte) 1);
        return true;
    }

    private static boolean isSpartan(Class<?> type) {
        for (Class<?> c = type; c != null; c = c.getSuperclass()) {
            if (c.getName().equals(SPARTAN)) {
                return true;
            }
        }
        return false;
    }

    @SuppressWarnings("unchecked")
    private static void find() {
        if (looked) {
            return;
        }
        looked = true;
        try {
            Field f = ThrownTrident.class.getDeclaredField("f_37558_");
            f.setAccessible(true);
            loyalty = (EntityDataAccessor<Byte>) f.get(null);
        } catch (ReflectiveOperationException ignored) {
            loyalty = null;
        }
        try {
            Field f = Class.forName(SPARTAN).getDeclaredField("DATA_RETURN");
            f.setAccessible(true);
            spartanReturn = (EntityDataAccessor<Byte>) f.get(null);
        } catch (ReflectiveOperationException | LinkageError ignored) {
            spartanReturn = null;
        }
    }
}
