package fotfskills.perk;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ThreadLocalRandom;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.tags.TagKey;
import net.minecraft.world.Container;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.event.entity.player.ItemFishedEvent;
import net.minecraftforge.event.entity.player.PlayerEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.items.ItemHandlerHelper;
import net.minecraftforge.registries.ForgeRegistries;

/** Crafting refunds (Frugal, Endless Workshop), Fletcher's extra arrows, and Double Catch. */
public final class ItemPerks {
    private static final TagKey<Item> ARROWS = TagKey.m_203882_(ForgeRegistries.Keys.ITEMS, new ResourceLocation("minecraft", "arrows"));

    /** Fires before the grid is consumed, so the ingredients are still there to copy. */
    @SubscribeEvent
    public void onCraft(PlayerEvent.ItemCraftedEvent event) {
        if (!(event.getEntity() instanceof ServerPlayer player)) {
            return;
        }
        Container grid = event.getInventory();
        List<ItemStack> refundable = new ArrayList<>();
        List<String> ids = new ArrayList<>();
        for (int i = 0; i < grid.m_6643_(); i++) {
            ItemStack stack = grid.m_8020_(i);
            if (!stack.m_41619_()) {
                ResourceLocation key = ForgeRegistries.ITEMS.getKey(stack.m_41720_());
                ids.add(key == null ? "" : key.toString());
                if (!stack.m_41720_().m_41470_()) {      // no bucket/bottle remainder
                    ItemStack one = stack.m_41777_();
                    one.m_41764_(1);
                    refundable.add(one);
                }
            }
        }
        if (Refund.eligible(ids) && !refundable.isEmpty()) {
            if (Perks.roll(player, "craft_free")) {
                refundable.forEach(stack -> ItemHandlerHelper.giveItemToPlayer(player, stack));
            } else if (Perks.roll(player, "craft_save")) {
                ItemHandlerHelper.giveItemToPlayer(player, refundable.get(ThreadLocalRandom.current().nextInt(refundable.size())));
            }
        }
        ItemStack result = event.getCrafting();
        if (result.m_204117_(ARROWS) && Perks.roll(player, "craft_arrows")) {
            ItemHandlerHelper.giveItemToPlayer(player, result.m_41777_());
        }
    }

    @SubscribeEvent
    public void onFished(ItemFishedEvent event) {
        if (event.getEntity() instanceof ServerPlayer player && Perks.roll(player, "double_catch")) {
            event.getDrops().forEach(stack -> ItemHandlerHelper.giveItemToPlayer(player, stack.m_41777_()));
        }
    }
}
