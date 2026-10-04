package fotfskills.perk;

import fotfskills.mixin.AbstractArrowAccessor;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.tags.TagKey;
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.world.entity.projectile.Projectile;
import net.minecraft.world.entity.projectile.ThrowableItemProjectile;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.registries.ForgeRegistries;

/**
 * Which player projectiles the Range perks apply to: arrows (an arrow entity whose item is in #minecraft:arrows) and
 * thrown weapons (whose item is in #fotfskills:thrown: tridents, javelins, tomahawks, knives). Spell projectiles,
 * ender pearls, fishing bobbers, snowballs and fireworks are OTHER and get nothing.
 */
public final class Projectiles {
    public enum Kind { ARROW, THROWN, OTHER }

    /** Created on first use, so the pure kind(...) rule can be tested without the game. */
    private static TagKey<Item> arrows;

    private Projectiles() {
    }

    public static Kind kind(boolean arrowEntity, boolean arrowItem, boolean thrownItem) {
        if (arrowEntity && arrowItem) {
            return Kind.ARROW;
        }
        return thrownItem ? Kind.THROWN : Kind.OTHER;
    }

    public static Kind kind(Projectile projectile) {
        if (arrows == null) {
            arrows = TagKey.m_203882_(ForgeRegistries.Keys.ITEMS, new ResourceLocation("minecraft", "arrows"));
        }
        ItemStack item = item(projectile);
        return kind(projectile instanceof AbstractArrow, item.m_204117_(arrows), Weapons.is(item, "thrown"));
    }

    /** The item a projectile stands for (arrow or thrown weapon pickup, or a thrown item's stack); EMPTY otherwise. */
    public static ItemStack item(Projectile projectile) {
        if (projectile instanceof AbstractArrow arrow) {
            return ((AbstractArrowAccessor) arrow).fotfskills$pickupItem();
        }
        if (projectile instanceof ThrowableItemProjectile thrown) {
            return thrown.m_7846_();
        }
        return ItemStack.f_41583_;
    }
}
