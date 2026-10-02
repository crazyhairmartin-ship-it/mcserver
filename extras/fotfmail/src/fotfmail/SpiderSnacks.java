package fotfmail;

import net.minecraft.resources.ResourceLocation;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.TamableAnimal;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.Level;
import net.minecraftforge.event.entity.player.PlayerInteractEvent;
import net.minecraftforge.registries.ForgeRegistries;

/**
 * Your tamed jumping spiders (Critters & Companions) heal 4 hearts from a spider eye or rotten flesh, like feeding a
 * wolf meat. Taming, breeding and tempting still only use dragonfly wings. Handled first (HIGHEST, even if another
 * mod already took the click) on both the precise and the normal entity click, so the jumping spider's own click
 * handling and eating the snack yourself never get in the way. A full-health spider just puffs smoke.
 */
final class SpiderSnacks {
    private static final ResourceLocation JUMPING_SPIDER = new ResourceLocation("crittersandcompanions", "jumping_spider");
    private static final float HEAL = 8.0F;

    private SpiderSnacks() {
    }

    static void onInteract(PlayerInteractEvent.EntityInteract event) {
        handle(event, event.getTarget());
    }

    static void onInteractAt(PlayerInteractEvent.EntityInteractSpecific event) {
        handle(event, event.getTarget());
    }

    private static void handle(PlayerInteractEvent event, Entity target) {
        ItemStack snack = event.getItemStack();
        if (!snack.m_150930_(Items.f_42591_) && !snack.m_150930_(Items.f_42583_)) {
            return;
        }
        if (!(target instanceof TamableAnimal spider) || !JUMPING_SPIDER.equals(ForgeRegistries.ENTITY_TYPES.getKey(target.m_6095_()))) {
            return;
        }
        Player player = event.getEntity();
        if (!spider.m_21824_() || !spider.m_21830_(player)) {
            return;
        }
        Level level = event.getLevel();
        event.setCanceled(true);
        event.setCancellationResult(InteractionResult.m_19078_(level.m_5776_()));
        if (level.m_5776_()) {
            return;
        }
        if (spider.m_21223_() >= spider.m_21233_()) {
            level.m_7605_(spider, (byte) 6); // smoke: not hungry
            return;
        }
        spider.m_5634_(HEAL);
        level.m_7605_(spider, (byte) 7); // hearts, as when taming
        spider.m_5496_(SoundEvents.f_11912_, 1.0F, 1.2F);
        if (!player.m_150110_().f_35937_) {
            snack.m_41774_(1);
        }
    }
}
