package fotfskills.client;

import fotfskills.perk.ClientBuffs;
import java.util.List;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.Font;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.gui.screens.inventory.InventoryScreen;
import net.minecraftforge.client.event.ScreenEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;

/** Lists the player's active situational skill buffs to the left of the survival inventory. */
public final class BuffsOverlay {
    private static final int IMAGE_WIDTH = 176;
    private static final int IMAGE_HEIGHT = 166;

    @SubscribeEvent
    public void onRender(ScreenEvent.Render.Post event) {
        Screen screen = event.getScreen();
        List<String> lines = ClientBuffs.get();
        if (!(screen instanceof InventoryScreen) || lines.isEmpty()) {
            return;
        }
        Font font = Minecraft.m_91087_().f_91062_;
        GuiGraphics graphics = event.getGuiGraphics();
        String title = "Active skill buffs";
        int width = font.m_92895_(title);
        for (String line : lines) {
            width = Math.max(width, font.m_92895_(line));
        }
        int left = (screen.f_96543_ - IMAGE_WIDTH) / 2 - width - 8;
        int top = (screen.f_96544_ - IMAGE_HEIGHT) / 2 + 4;
        if (left < 2) {
            left = 2;
            top = 2;
        }
        graphics.m_280056_(font, title, left, top, 0xFFE3B341, true);
        int y = top + 12;
        for (String line : lines) {
            graphics.m_280056_(font, line, left, y, 0xFFFFFFFF, true);
            y += 10;
        }
    }
}
