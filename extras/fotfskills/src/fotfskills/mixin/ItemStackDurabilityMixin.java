package fotfskills.mixin;

import fotfskills.perk.Chance;
import fotfskills.perk.Perks;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.util.RandomSource;
import net.minecraft.world.item.ArmorItem;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.PickaxeItem;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.ModifyVariable;

/** Steady Pick / Armour Care / Unbreakable: each point of durability loss may be saved. ItemStack.hurt = m_220157_. */
@Mixin(value = ItemStack.class, remap = false)
public abstract class ItemStackDurabilityMixin {
    @ModifyVariable(method = "m_220157_", at = @At("HEAD"), ordinal = 0, argsOnly = true, remap = false)
    private int fotfskills$saveDurability(int amount, int ignored, RandomSource random, ServerPlayer player) {
        if (player == null || amount <= 0) {
            return amount;
        }
        ItemStack stack = (ItemStack) (Object) this;
        if (stack.m_41783_() != null && stack.m_41783_().m_128441_(fotfskills.perk.CraftPerks.SMITH)) {
            amount = Chance.reduce(amount, stack.m_41783_().m_128457_(fotfskills.perk.CraftPerks.SMITH), Perks::random);
        }
        Object item = stack.m_41720_();
        String perk = item instanceof PickaxeItem ? "pickaxe_durability" : item instanceof ArmorItem ? "armour_durability" : null;
        return perk == null ? amount : Chance.reduce(amount, Perks.get(player, perk), Perks::random);
    }
}
