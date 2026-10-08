package fotfskills.compat;

import com.obscura.storage.gui.StorageTerminalMenu;
import com.obscura.storage.tile.StorageTerminalBlockEntity;
import com.obscura.storage.util.ItemKey;
import com.obscura.storage.util.StorageSnapshot;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.item.ItemStack;

/**
 * "Move matching items" for Obscura's Simple Storage terminals (Inventory Profiles Next's version only works on real
 * container slots, and the terminal's grid isn't one): every stack in the player's main inventory whose item the
 * network already holds goes into the network. The hotbar stays put. Sent by client/TerminalDepositButton.
 */
public final class TerminalDeposit {
    private TerminalDeposit() {
    }

    public static void depositMatching(ServerPlayer player) {
        if (!(player.f_36096_ instanceof StorageTerminalMenu menu)) {
            return;
        }
        StorageTerminalBlockEntity terminal = menu.getTerminal();
        if (terminal == null || !terminal.canInteractWith(player, false)) {
            return;
        }
        StorageSnapshot stored = terminal.getSnapshot();
        Inventory inv = player.m_150109_();
        for (int i = Inventory.m_36059_(); i < 36; i++) {          // 9..35: main inventory, not the hotbar
            ItemStack stack = inv.f_35974_.get(i);
            if (!stack.m_41619_() && stored.contains(ItemKey.of(stack))) {
                inv.f_35974_.set(i, terminal.pushStack(stack.m_41777_()));
            }
        }
        menu.m_38946_();
    }
}
