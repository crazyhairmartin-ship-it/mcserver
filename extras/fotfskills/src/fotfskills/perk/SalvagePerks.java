package fotfskills.perk;

import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.inventory.GrindstoneMenu;
import net.minecraft.world.item.ArmorItem;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TieredItem;
import net.minecraft.world.item.crafting.Ingredient;
import net.minecraftforge.event.GrindstoneEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.items.ItemHandlerHelper;
import net.minecraftforge.server.ServerLifecycleHooks;

/**
 * Salvager: taking a disenchanted tool, weapon or armour piece out of a grindstone may also give back one of its repair
 * material (iron ingot, diamond, leather...). Only enchanted inputs count, so plain gear can't be ground for materials.
 * Forge's grindstone event has no player, so the player is the one whose open grindstone holds those exact items.
 */
public final class SalvagePerks {
    @SubscribeEvent
    public void onTake(GrindstoneEvent.OnTakeItem event) {
        MinecraftServer server = ServerLifecycleHooks.getCurrentServer();
        if (server == null || !server.m_18695_()) {
            return;
        }
        for (ServerPlayer player : server.m_6846_().m_11314_()) {
            if (player.f_36096_ instanceof GrindstoneMenu menu
                    && (menu.m_38853_(0).m_7993_() == event.getTopItem() || menu.m_38853_(1).m_7993_() == event.getBottomItem())) {
                salvage(player, event.getTopItem());
                salvage(player, event.getBottomItem());
                return;
            }
        }
    }

    private static void salvage(ServerPlayer player, ItemStack input) {
        if (input.m_41619_() || !input.m_41793_() || !Perks.roll(player, "salvager")) {
            return;
        }
        Ingredient repair = input.m_41720_() instanceof TieredItem tiered ? tiered.m_43314_().m_6282_()
                : input.m_41720_() instanceof ArmorItem armor ? armor.m_40401_().m_6230_() : Ingredient.f_43901_;
        ItemStack[] options = repair.m_43908_();
        if (options.length > 0) {
            ItemHandlerHelper.giveItemToPlayer(player, options[0].m_255036_(1));
        }
    }
}
