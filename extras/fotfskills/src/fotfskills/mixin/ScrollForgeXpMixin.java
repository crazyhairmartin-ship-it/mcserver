package fotfskills.mixin;

import fotfskills.xp.AmountSource;
import io.redspace.ironsspellbooks.api.spells.ISpellContainer;
import io.redspace.ironsspellbooks.api.spells.SpellData;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * Magic XP for inscribing a scroll at Iron's Scroll Forge (its result slot; clicks and shift-clicks both take through
 * here). Amount = the spell's rarity at that level, 1 (common) to 5 (legendary), times inscribe_scroll's per_rarity in
 * config/puffish_skills/categories/magic/experience.json.
 */
@Mixin(targets = "io.redspace.ironsspellbooks.gui.scroll_forge.ScrollForgeMenu$4", remap = false)
public abstract class ScrollForgeXpMixin {
    @Inject(method = "m_142406_", remap = false, at = @At("TAIL"))
    private void fotfskills$inscribed(Player player, ItemStack scroll, CallbackInfo ci) {
        if (!(player instanceof ServerPlayer server) || scroll.m_41619_()) {
            return;
        }
        ISpellContainer spells = ISpellContainer.get(scroll);
        SpellData spell = spells == null ? null : spells.getSpellAtIndex(0);
        int rarity = spell == null || spell.getSpell() == null ? 0 : spell.getSpell().getRarity(spell.getLevel()).ordinal();
        AmountSource.award(server, "inscribe_scroll", rarity + 1);
    }
}
