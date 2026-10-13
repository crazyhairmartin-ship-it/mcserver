package fotfskills.perk;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ThreadLocalRandom;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.tags.TagKey;
import net.minecraft.world.Container;
import net.minecraft.world.inventory.CraftingContainer;
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
    private static final TagKey<Item> NOT_WORKSTATIONS = TagKey.m_203882_(ForgeRegistries.Keys.ITEMS, new ResourceLocation("fotfskills", "not_workstations"));
    private static final TagKey<Item> WORKSTATIONS = TagKey.m_203882_(ForgeRegistries.Keys.ITEMS, new ResourceLocation("fotfskills", "workstations"));

    /** Fires before the grid is consumed, so the ingredients are still there to copy. */
    /**
     * Workstations and storage: any block with a block entity (chests, barrels, furnaces, cooking stations, modded
     * storage), plus #fotfskills:workstations for the tables without one (crafting table, loom, stonecutter...), minus
     * #fotfskills:not_workstations (signs, beds, banners, heads).
     */
    private static boolean isWorkstation(ItemStack stack) {
        if (stack.m_204117_(NOT_WORKSTATIONS)) {
            return false;
        }
        return stack.m_204117_(WORKSTATIONS) || stack.m_41720_() instanceof net.minecraft.world.item.BlockItem block
                && block.m_40614_() instanceof net.minecraft.world.level.block.EntityBlock;
    }

    @SubscribeEvent
    public void onCraft(PlayerEvent.ItemCraftedEvent event) {
        if (!(event.getEntity() instanceof ServerPlayer player)) {
            return;
        }
        Container grid = event.getInventory();
        boolean craftingGrid = grid instanceof CraftingContainer;   // not Tinkers stations/worktables (tool in slot 0)
        List<ItemStack> refundable = new ArrayList<>();
        List<String> ids = new ArrayList<>();
        for (int i = 0; i < grid.m_6643_(); i++) {
            ItemStack stack = grid.m_8020_(i);
            if (!stack.m_41619_()) {
                ResourceLocation key = ForgeRegistries.ITEMS.getKey(stack.m_41720_());
                ids.add(key == null ? "" : key.toString());
                if (!stack.m_41720_().m_41470_()
                        && Refund.refundableStack(stack.m_41763_(), stack.m_41741_(), stack.m_41782_())) {
                    ItemStack one = stack.m_41777_();
                    one.m_41764_(1);
                    refundable.add(one);
                }
            }
        }
        if (craftingGrid && Refund.eligible(ids)) {
            fotfskills.xp.AmountSource.award(player, "craft_any", 1);    // any real recipe (no compress/decompress loops)
        }
        ItemStack made = event.getCrafting();
        if (craftingGrid && isWorkstation(made)) {
            fotfskills.xp.AmountSource.award(player, "craft_utility", ids.size());   // per ingredient used
        }
        if (craftingGrid && made.m_41614_() && ids.size() >= 2 && made.m_41613_() <= ids.size()) {
            net.minecraft.world.food.FoodProperties food = made.m_41720_().m_41473_();   // food crafted in a grid: Cooking
            if (food != null) {                                                     // (never unpacking a crate)
                fotfskills.xp.AmountSource.award(player, "cook", (double) food.m_38744_() * made.m_41613_());
            }
        }
        if (craftingGrid && Refund.eligible(ids) && !refundable.isEmpty()) {
            if (Perks.roll(player, "craft_free")) {
                refundable.forEach(stack -> ItemHandlerHelper.giveItemToPlayer(player, stack));
            } else if (Perks.random() < saveChance(player, event.getCrafting())) {
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

    /** Frugal for any craft, plus Thrifty Cook for food and Spellwright for Iron's items. */
    private static double saveChance(ServerPlayer player, ItemStack result) {
        ResourceLocation key = ForgeRegistries.ITEMS.getKey(result.m_41720_());
        String ns = key == null ? "" : key.m_135827_();
        double chance = Perks.get(player, "craft_save");
        if (result.m_41614_()) {
            chance += Perks.get(player, "cook_save");
        }
        if (ns.equals("irons_spellbooks")) {
            chance += Perks.get(player, "spell_save");
        }
        return Math.min(chance, 0.95);
    }
}
