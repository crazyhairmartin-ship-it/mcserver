package fotfskills.client;

import fotfskills.mixin.ContainerScreenAccessor;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.components.Tooltip;
import net.minecraft.client.gui.screens.inventory.InventoryScreen;
import net.minecraft.network.chat.Component;
import net.minecraftforge.client.event.ScreenEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;

/**
 * A small button at the top right of the survival inventory opens the skill buffs screen (BuffsScreen). The button follows
 * the inventory when the recipe book slides it sideways.
 */
public final class BuffsOverlay {
    private Button button;

    @SubscribeEvent
    public void onInit(ScreenEvent.Init.Post event) {
        if (!(event.getScreen() instanceof InventoryScreen inventory)) {
            return;
        }
        button = Button.m_253074_(Component.m_237113_("✦"), b -> Minecraft.m_91087_().m_91152_(new CharacterScreen(inventory)))
                .m_252987_(0, 0, 16, 16)
                .m_257505_(Tooltip.m_257550_(Component.m_237113_("Character: skills, buffs, health, stamina and mana")))
                .m_253136_();
        place(inventory);
        event.addListener(button);
    }

    @SubscribeEvent
    public void onRender(ScreenEvent.Render.Pre event) {
        if (event.getScreen() instanceof InventoryScreen inventory && button != null) {
            place(inventory);
        }
    }

    private void place(InventoryScreen inventory) {
        ContainerScreenAccessor panel = (ContainerScreenAccessor) inventory;
        button.m_252865_(panel.fotfskills$left() + panel.fotfskills$width() + 2);
        button.m_253211_(panel.fotfskills$top() + 2);
    }
}
