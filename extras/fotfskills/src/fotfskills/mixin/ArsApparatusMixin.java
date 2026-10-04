package fotfskills.mixin;

import fotfskills.perk.Perks;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Redirect;

/**
 * Sourcecraft: the enchanting apparatus asks less source of a player with the perk (10% less per rank). Both the
 * "enough source nearby?" check and the charge read the recipe's cost, so both see the reduced cost.
 */
@Pseudo
@Mixin(targets = "com.hollingsworth.arsnouveau.common.block.tile.EnchantingApparatusTile", remap = false)
public abstract class ArsApparatusMixin {
    @Redirect(method = {"attemptCraft", "craftingPossible"}, remap = false, require = 0, at = @At(value = "INVOKE", remap = false,
            target = "Lcom/hollingsworth/arsnouveau/api/enchanting_apparatus/IEnchantingRecipe;getSourceCost()I"))
    private int fotfskills$cheaperCraft(com.hollingsworth.arsnouveau.api.enchanting_apparatus.IEnchantingRecipe recipe,
                                        ItemStack stack, Player player) {
        int cost = recipe.getSourceCost();
        double off = player == null ? 0 : Math.min(0.9, Perks.get(player, "apparatus_save"));
        return (int) Math.round(cost * (1 - off));
    }
}
