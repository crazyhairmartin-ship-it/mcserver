package fotfskills.client;

import com.obscura.storage.gui.AbstractStorageTerminalScreen;
import fotfskills.perk.PerkSync;
import net.minecraft.client.gui.components.AbstractWidget;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.components.Tooltip;
import net.minecraft.network.chat.Component;
import net.minecraftforge.client.event.ScreenEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;

/** A "move matching items into storage" button under Obscura's terminal buttons (see compat/TerminalDeposit). */
public final class TerminalDepositButton {
    @SubscribeEvent
    public void onInit(ScreenEvent.Init.Post event) {
        if (!(event.getScreen() instanceof AbstractStorageTerminalScreen<?>)) {
            return;
        }
        int x = Integer.MAX_VALUE;
        for (var listener : event.getListenersList()) {                     // Obscura's buttons run down the left edge
            if (listener instanceof AbstractWidget w) {
                x = Math.min(x, w.m_252754_());
            }
        }
        if (x == Integer.MAX_VALUE) {
            return;
        }
        int bottom = 0;
        int width = 16;
        for (var listener : event.getListenersList()) {
            if (listener instanceof AbstractWidget w && w.m_252754_() == x) {
                bottom = Math.max(bottom, w.m_252907_() + w.m_93694_());
                if (w.m_5711_() >= 12 && w.m_5711_() <= 24) {       // vanilla buttons under ~4px tall crash when drawn
                    width = w.m_5711_();
                }
            }
        }
        event.addListener(new Button.Builder(Component.m_237113_("⇩"), b -> PerkSync.sendDepositMatching())
                .m_252987_(x, bottom + 2, width, width)
                .m_257505_(Tooltip.m_257550_(Component.m_237113_("Move matching items into storage\n(your hotbar stays put)")))
                .m_253136_());
    }
}
