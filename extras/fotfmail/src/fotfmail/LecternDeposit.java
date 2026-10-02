package fotfmail;

import com.hollingsworth.arsnouveau.client.container.StorageTerminalMenu;
import com.hollingsworth.arsnouveau.common.block.tile.StorageLecternTile;
import fotfmail.mixin.StorageTerminalMenuAccessor;
import java.util.Set;
import java.util.function.Supplier;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.network.NetworkEvent;

/**
 * "Move matching items" for Ars Nouveau's Storage Lectern (client -> server, from the button added by
 * AbstractStorageTerminalScreenMixin): every stack in the main inventory (not the hotbar) whose item is already
 * stored in the lectern's network goes in, like Inventory Profiles Next's button does for normal chests. IPN's own
 * buttons can't, because the lectern shows a virtual list instead of real container slots.
 */
public final class LecternDeposit {
    private static final int MAIN_INVENTORY_START = 9;
    private static final int MAIN_INVENTORY_END = 36;

    static void encode(LecternDeposit message, FriendlyByteBuf buffer) {
    }

    static LecternDeposit decode(FriendlyByteBuf buffer) {
        return new LecternDeposit();
    }

    static void handle(LecternDeposit message, Supplier<NetworkEvent.Context> context) {
        context.get().enqueueWork(() -> {
            ServerPlayer player = context.get().getSender();
            if (player != null && player.f_36096_ instanceof StorageTerminalMenu menu) {
                depositMatching(player, menu);
            }
        });
        context.get().setPacketHandled(true);
    }

    private static void depositMatching(ServerPlayer player, StorageTerminalMenu menu) {
        StorageLecternTile lectern = ((StorageTerminalMenuAccessor) menu).fotfmail$lectern();
        if (lectern == null) {
            return;
        }
        Set<Item> stored = lectern.itemCounts.keySet();
        Inventory inventory = player.m_150109_();
        for (int slot = MAIN_INVENTORY_START; slot < MAIN_INVENTORY_END; slot++) {
            ItemStack stack = inventory.m_8020_(slot);
            if (stack.m_41619_() || !stored.contains(stack.m_41720_())) {
                continue;
            }
            inventory.m_6836_(slot, lectern.pushStack(stack.m_41777_(), menu.selectedTab));
        }
        menu.m_38946_();
    }
}
