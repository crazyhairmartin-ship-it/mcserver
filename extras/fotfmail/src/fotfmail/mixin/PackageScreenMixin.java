package fotfmail.mixin;

import com.chaosthedude.endermail.gui.PackageScreen;
import com.chaosthedude.endermail.gui.container.PackageMenu;
import fotfmail.FotfMail;
import fotfmail.SendPackagePacket;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.components.EditBox;
import net.minecraft.client.gui.screens.inventory.AbstractContainerScreen;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.phys.BlockHitResult;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;

/**
 * The package screen gets the mailbox screen's layout: its 5 slots on the left (PackageMenuMixin) and, on the
 * right, a Recipient box (a mailbox ID, like the mailbox's own ID box) with a Send button. Send / Enter asks the
 * server to send the package there (SendPackagePacket) and closes the screen.
 * init = m_7856_, keyPressed = m_7933_, renderLabels = m_280003_ (PackageScreen doesn't declare any of them).
 */
@Mixin(PackageScreen.class)
public abstract class PackageScreenMixin extends AbstractContainerScreen<PackageMenu> {
    @Unique
    private EditBox fotfmail$recipient;
    @Unique
    private BlockPos fotfmail$packagePos;

    protected PackageScreenMixin(PackageMenu menu, Inventory inventory, Component title) {
        super(menu, inventory, title);
    }

    @Override
    protected void m_7856_() {
        super.m_7856_();
        if (Minecraft.m_91087_().f_91077_ instanceof BlockHitResult hit) {
            fotfmail$packagePos = hit.m_82425_();
        }
        fotfmail$recipient = new EditBox(f_96547_, f_97735_ + 102, f_97736_ + 20, 44, 18, Component.m_237113_(""));
        fotfmail$recipient.m_94199_(12);
        m_142416_(fotfmail$recipient);
        m_142416_(Button.m_253074_(Component.m_237115_("fotfmail.package.send"), button -> fotfmail$send())
                .m_252987_(f_97735_ + 148, f_97736_ + 19, 22, 20).m_253136_());
    }

    @Unique
    private void fotfmail$send() {
        String recipient = fotfmail$recipient.m_94155_().trim();
        if (fotfmail$packagePos == null || recipient.isEmpty()) {
            fotfmail$recipient.m_93692_(true);
            return;
        }
        FotfMail.NETWORK.sendToServer(new SendPackagePacket(fotfmail$packagePos, recipient));
        m_7379_();
    }

    @Override
    public boolean m_7933_(int key, int scanCode, int modifiers) {
        if (fotfmail$recipient != null && fotfmail$recipient.m_93696_() && key != 256) {
            if (key == 257 || key == 335) {
                fotfmail$send();
                return true;
            }
            return fotfmail$recipient.m_7933_(key, scanCode, modifiers) || fotfmail$recipient.m_94204_();
        }
        return super.m_7933_(key, scanCode, modifiers);
    }

    @Override
    protected void m_280003_(GuiGraphics graphics, int mouseX, int mouseY) {
        super.m_280003_(graphics, mouseX, mouseY);
        graphics.m_280614_(f_96547_, Component.m_237115_("fotfmail.package.recipient"), 102, 9, 4210752, false);
    }
}
