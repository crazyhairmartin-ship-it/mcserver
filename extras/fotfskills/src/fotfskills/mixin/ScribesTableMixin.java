package fotfskills.mixin;

import fotfskills.perk.Perks;
import net.minecraft.world.entity.player.Player;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Redirect;

/**
 * Artificer: glyphs cost less XP at Ars Nouveau's Scribe's Table. setRecipe reads the recipe's exp three times (the
 * "enough XP?" check and the charge); every read returns the reduced cost.
 */
@Pseudo
@Mixin(targets = "com.hollingsworth.arsnouveau.common.block.tile.ScribesTile", remap = false)
public abstract class ScribesTableMixin {
    @Redirect(method = "setRecipe", remap = false, require = 0, at = @At(value = "FIELD", opcode = 180 /* GETFIELD */,
            target = "Lcom/hollingsworth/arsnouveau/common/crafting/recipes/GlyphRecipe;exp:I", remap = false))
    private int fotfskills$cheaperGlyph(com.hollingsworth.arsnouveau.common.crafting.recipes.GlyphRecipe recipe,
                                        com.hollingsworth.arsnouveau.common.crafting.recipes.GlyphRecipe chosen, Player player) {
        double off = Math.min(0.9, Perks.get(player, "artificer_glyph"));
        return (int) Math.round(recipe.exp * (1 - off));
    }
}
