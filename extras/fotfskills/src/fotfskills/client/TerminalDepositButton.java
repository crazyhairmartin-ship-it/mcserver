package fotfskills.client;

import com.obscura.storage.gui.AbstractStorageTerminalScreen;
import fotfskills.mixin.ContainerScreenAccessor;
import fotfskills.perk.PerkSync;
import net.minecraft.client.gui.components.AbstractWidget;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.components.Tooltip;
import net.minecraft.network.chat.Component;
import net.minecraftforge.client.event.ScreenEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;

/**
 * A "move matching items into storage" button under Obscura's terminal buttons (see compat/TerminalDeposit), on the
 * storage and crafting terminals alike. Obscura's buttons run down the left side of the panel; other mods put widgets
 * elsewhere on the screen (even at its corner), so only widgets just left of the panel count.
 */
public final class TerminalDepositButton {
    private static final int SIZE = 16;

    @SubscribeEvent
    public void onInit(ScreenEvent.Init.Post event) {
        if (!(event.getScreen() instanceof AbstractStorageTerminalScreen<?> screen)) {
            return;
        }
        ContainerScreenAccessor panel = (ContainerScreenAccessor) screen;
        int left = panel.fotfskills$left();
        int top = panel.fotfskills$top();
        int x = Integer.MAX_VALUE;
        int bottom = top;
        for (var listener : event.getListenersList()) {
            if (listener instanceof AbstractWidget w && column(w, left, top)) {
                x = Math.min(x, w.m_252754_());
                bottom = Math.max(bottom, w.m_252907_() + w.m_93694_());
            }
        }
        if (x == Integer.MAX_VALUE) {
            x = left - SIZE - 4;                                         // no column found: sit beside the panel
        }
        event.addListener(new Button.Builder(Component.m_237113_("⇩"), b -> PerkSync.sendDepositMatching())
                .m_252987_(x, bottom + 2, SIZE, SIZE)
                .m_257505_(Tooltip.m_257550_(Component.m_237113_("Move matching items into storage\n(your hotbar stays put)")))
                .m_253136_());
    }

    /** A button-sized widget in the strip just left of the panel, below its top edge. */
    private static boolean column(AbstractWidget w, int left, int top) {
        int wx = w.m_252754_();
        int width = w.m_5711_();
        return width >= 8 && width <= 24 && w.m_93694_() >= 8
                && wx + width <= left && wx >= left - 40 && w.m_252907_() >= top - 4;
    }
}
