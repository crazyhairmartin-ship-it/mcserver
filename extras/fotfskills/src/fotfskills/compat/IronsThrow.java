package fotfskills.compat;

import net.minecraft.world.entity.Entity;
import net.minecraft.world.item.ItemStack;

/**
 * Iron's Throw spell flings the caster's weapon (a ThrownItemProjectile carrying it); its hits count as hits with that
 * weapon for the weapon perks (perk/WeaponPerks, CombatPerks' Executioner). Iron's classes are only touched once the
 * projectile's class name matches, so this is safe without Iron's.
 */
public final class IronsThrow {
    private static final String THROWN = "io.redspace.ironsspellbooks.entity.spells.thrown_item.ThrownItemProjectile";

    private IronsThrow() {
    }

    /** The weapon a Throw projectile carries, or EMPTY for anything else. */
    public static ItemStack weapon(Entity direct) {
        if (direct == null || !THROWN.equals(direct.getClass().getName())) {
            return ItemStack.f_41583_;
        }
        return Irons.item(direct);
    }

    private static final class Irons {
        static ItemStack item(Entity direct) {
            ItemStack stack = ((io.redspace.ironsspellbooks.entity.spells.thrown_item.ThrownItemProjectile) direct).getThrownItem();
            return stack == null ? ItemStack.f_41583_ : stack;
        }
    }
}
