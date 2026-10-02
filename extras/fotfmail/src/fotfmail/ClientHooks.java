package fotfmail;

import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.screens.inventory.BookEditScreen;
import net.minecraft.client.gui.screens.inventory.BookViewScreen;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;

/** Client-only: only ever called when level.isClientSide(), so these screen classes never load on a server. */
final class ClientHooks {
    private ClientHooks() {
    }

    static void openLetter(Player player, ItemStack stack, InteractionHand hand) {
        if (LetterItem.isSigned(stack)) {
            Minecraft.m_91087_().m_91152_(new BookViewScreen(new BookViewScreen.WrittenBookAccess(stack)));
        } else {
            Minecraft.m_91087_().m_91152_(new BookEditScreen(player, stack, hand));
        }
    }
}
