package fotfskills.client;

import fotfskills.perk.ClientBuffs;
import java.util.List;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;

/** Your active situational skill buffs and total level, opened from the inventory (Back or Esc returns there). */
public final class BuffsScreen extends Screen {
    private final Screen parent;

    public BuffsScreen(Screen parent) {
        super(Component.m_237113_("Skill buffs"));
        this.parent = parent;
    }

    @Override
    protected void m_7856_() {
        m_142416_(Button.m_253074_(Component.m_237113_("Back"), b -> m_7379_())
                .m_252987_(f_96543_ / 2 - 50, f_96544_ - 32, 100, 20).m_253136_());
    }

    @Override
    public void m_88315_(GuiGraphics graphics, int mouseX, int mouseY, float partialTick) {
        m_280273_(graphics);
        graphics.m_280137_(f_96547_, "§6§lSkill buffs", f_96543_ / 2, 24, 0xFFFFFFFF);
        List<String> lines = ClientBuffs.get();
        int y = 48;
        if (lines.isEmpty()) {
            graphics.m_280137_(f_96547_, "§7No situational buffs are active right now.", f_96543_ / 2, y, 0xFFFFFFFF);
        }
        for (String line : lines) {
            graphics.m_280137_(f_96547_, line, f_96543_ / 2, y, 0xFFFFFFFF);
            y += 12;
        }
        super.m_88315_(graphics, mouseX, mouseY, partialTick);
    }

    @Override
    public void m_7379_() {
        f_96541_.m_91152_(parent);
    }
}
