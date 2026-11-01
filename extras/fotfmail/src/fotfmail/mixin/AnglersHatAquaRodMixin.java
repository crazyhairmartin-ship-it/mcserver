package fotfmail.mixin;

import artifacts.item.wearable.WearableArtifactItem;
import artifacts.registry.ModGameRules;
import artifacts.registry.ModItems;
import com.teammetallurgy.aquaculture.item.AquaFishingRodItem;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.enchantment.EnchantmentHelper;
import net.minecraft.world.level.Level;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Redirect;

/**
 * Artifacts' Angler's Hat (+Luck of the Sea, +Lure, set by its game rules) works on Aquaculture rods too. Artifacts
 * adds the bonus in the vanilla FishingRodItem.use, but Aquaculture's rods replace use() with their own, which reads
 * Luck of the Sea and Lure itself, so the hat did nothing there. Same rules as Artifacts: the hat has to be worn, and
 * Lure tops out at 5. Dylan, 2026-11-01.
 */
@Mixin(value = AquaFishingRodItem.class, remap = false)
public abstract class AnglersHatAquaRodMixin {
    @Redirect(method = "m_7203_", remap = false, at = @At(value = "INVOKE", remap = false,
            target = "Lnet/minecraft/world/item/enchantment/EnchantmentHelper;m_44904_(Lnet/minecraft/world/item/ItemStack;)I"))
    private int fotfmail$hatLuck(ItemStack rod, Level level, Player player, InteractionHand hand) {
        int luck = EnchantmentHelper.m_44904_(rod);
        return fotfmail$wearsHat(player) ? luck + ModGameRules.ANGLERS_HAT_LUCK_OF_THE_SEA_LEVEL_BONUS.get() : luck;
    }

    @Redirect(method = "m_7203_", remap = false, at = @At(value = "INVOKE", remap = false,
            target = "Lnet/minecraft/world/item/enchantment/EnchantmentHelper;m_44916_(Lnet/minecraft/world/item/ItemStack;)I"))
    private int fotfmail$hatLure(ItemStack rod, Level level, Player player, InteractionHand hand) {
        int lure = EnchantmentHelper.m_44916_(rod);
        if (lure >= 5 || !fotfmail$wearsHat(player)) {
            return lure;
        }
        return Math.min(5, lure + ModGameRules.ANGLERS_HAT_LURE_LEVEL_BONUS.get());
    }

    private static boolean fotfmail$wearsHat(Player player) {
        return ((WearableArtifactItem) ModItems.ANGLERS_HAT.get()).isEquippedBy(player);
    }
}
