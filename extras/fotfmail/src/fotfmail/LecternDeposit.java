package fotfmail;

import com.hollingsworth.arsnouveau.client.container.StorageTerminalMenu;
import com.hollingsworth.arsnouveau.client.container.StoredItemStack;
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
 * The Storage Lectern's two extra buttons (client -> server, added by AbstractStorageTerminalScreenMixin), like
 * Inventory Profiles Next's buttons for normal chests. IPN's own buttons can't, because the lectern shows a virtual
 * list instead of real container slots.
 * - Move matching items (restock = false): every stack in the main inventory (not the hotbar) whose item is already
 *   stored in the lectern's network goes in.
 * - Restock (restock = true): every partial stack in the whole inventory (hotbar included) is topped up to a full
 *   stack from storage, if storage has more of that exact item.
 */
public final class LecternDeposit {
    private static final int MAIN_INVENTORY_START = 9;
    private static final int MAIN_INVENTORY_END = 36;

    private final boolean restock;

    public LecternDeposit(boolean restock) {
        this.restock = restock;
    }

    static void encode(LecternDeposit message, FriendlyByteBuf buffer) {
        buffer.writeBoolean(message.restock);
    }

    static LecternDeposit decode(FriendlyByteBuf buffer) {
        return new LecternDeposit(buffer.readBoolean());
    }

    static void handle(LecternDeposit message, Supplier<NetworkEvent.Context> context) {
        context.get().enqueueWork(() -> {
            ServerPlayer player = context.get().getSender();
            if (player != null && player.f_36096_ instanceof StorageTerminalMenu menu) {
                StorageLecternTile lectern = ((StorageTerminalMenuAccessor) menu).fotfmail$lectern();
                if (lectern != null) {
                    if (message.restock) {
                        restock(player, menu, lectern);
                    } else {
                        depositMatching(player, menu, lectern);
                    }
                    menu.m_38946_();
                }
            }
        });
        context.get().setPacketHandled(true);
    }

    private static void depositMatching(ServerPlayer player, StorageTerminalMenu menu, StorageLecternTile lectern) {
        Set<Item> stored = lectern.itemCounts.keySet();
        Inventory inventory = player.m_150109_();
        for (int slot = MAIN_INVENTORY_START; slot < MAIN_INVENTORY_END; slot++) {
            ItemStack stack = inventory.m_8020_(slot);
            if (stack.m_41619_() || !stored.contains(stack.m_41720_())) {
                continue;
            }
            inventory.m_6836_(slot, lectern.pushStack(stack.m_41777_(), menu.selectedTab));
        }
    }

    private static void restock(ServerPlayer player, StorageTerminalMenu menu, StorageLecternTile lectern) {
        Set<Item> stored = lectern.itemCounts.keySet();
        Inventory inventory = player.m_150109_();
        for (int slot = 0; slot < MAIN_INVENTORY_END; slot++) {
            ItemStack stack = inventory.m_8020_(slot);
            int missing = stack.m_41741_() - stack.m_41613_();
            if (stack.m_41619_() || missing <= 0 || !stored.contains(stack.m_41720_())) {
                continue;
            }
            StoredItemStack pulled = lectern.pullStack(new StoredItemStack(stack.m_255036_(1)), missing, menu.selectedTab);
            if (pulled == null) {
                continue;
            }
            ItemStack got = pulled.getActualStack();
            if (ItemStack.m_150942_(stack, got)) {
                int fits = Math.min(got.m_41613_(), missing);
                stack.m_41769_(fits);
                got.m_41774_(fits);
            }
            if (!got.m_41619_()) {
                // Storage handed back more than fits, or a different item: keep it rather than lose it.
                lectern.pushOrDrop(got, menu.selectedTab);
            }
        }
    }
}
