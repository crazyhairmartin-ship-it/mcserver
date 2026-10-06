package fotfars;

import com.hollingsworth.arsnouveau.client.container.StoredItemStack;
import java.util.HashMap;
import java.util.Map;
import net.minecraft.client.Minecraft;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.CreativeModeTabs;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;

/**
 * Client-only third sort mode for Ars Nouveau's Storage Lectern: items in the order they appear in the creative
 * inventory (tab by tab, then each tab's own order), ties broken alphabetically. Items in no creative tab go last.
 * Wired in by mixin/AbstractStorageTerminalScreenMixin; sort type 2 (Ars's own are 0 = amount, 1 = name).
 */
public final class CreativeTabSort implements StoredItemStack.IStoredItemStackComparator {
    public static final int TYPE = 2;
    private static Map<Item, Integer> order;
    private boolean reversed;

    public CreativeTabSort(boolean reversed) {
        this.reversed = reversed;
    }

    /** Rebuilds the creative order next time it's needed (each time the mode is picked or the screen syncs). */
    public static void reset() {
        order = null;
    }

    private static int index(ItemStack stack) {
        if (order == null) {
            order = build();
        }
        return order.getOrDefault(stack.m_41720_(), Integer.MAX_VALUE);
    }

    private static Map<Item, Integer> build() {
        Minecraft mc = Minecraft.m_91087_();
        if (mc.f_91074_ != null && mc.f_91073_ != null) {
            // Same call the creative inventory makes, so tab contents exist even if it was never opened.
            CreativeModeTabs.m_269226_(mc.f_91074_.f_108617_.m_247016_(),
                    mc.f_91066_.m_257871_().m_231551_() && mc.f_91074_.m_36337_(), mc.f_91073_.m_9598_());
        }
        Map<Item, Integer> result = new HashMap<>();
        int i = 0;
        for (CreativeModeTab tab : CreativeModeTabs.m_257478_()) {
            if (tab.m_257962_() != CreativeModeTab.Type.CATEGORY) {
                continue;
            }
            for (ItemStack stack : tab.m_260957_()) {
                result.putIfAbsent(stack.m_41720_(), i++);
            }
        }
        return result;
    }

    @Override
    public int compare(StoredItemStack a, StoredItemStack b) {
        int c = Integer.compare(index(a.getStack()), index(b.getStack()));
        if (c == 0) {
            c = a.getDisplayName().compareToIgnoreCase(b.getDisplayName());
        }
        return reversed ? -c : c;
    }

    @Override
    public boolean isReversed() {
        return reversed;
    }

    @Override
    public void setReversed(boolean reversed) {
        this.reversed = reversed;
    }

    @Override
    public int type() {
        return TYPE;
    }
}
