package fotfmail.mixin;

import fotfmail.LetterItem;
import java.util.List;
import net.minecraft.nbt.StringTag;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.server.network.FilteredText;
import net.minecraft.server.network.ServerGamePacketListenerImpl;
import net.minecraft.world.item.ItemStack;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * Vanilla only saves/signs book-screen edits for writable books; this does the same for letters.
 * m_9812_ = updateBookContents(pages, slot), m_215208_ = signBook(title, pages, slot), f_9743_ = player.
 * A signed letter stays a letter (one item), with title = recipient mailbox ID and author = writer.
 */
@Mixin(ServerGamePacketListenerImpl.class)
public abstract class ServerGamePacketListenerImplMixin {
    @Shadow(remap = false)
    public ServerPlayer f_9743_;

    @Inject(method = "m_9812_", at = @At("HEAD"), cancellable = true, remap = false)
    private void fotfmail$saveLetter(List<FilteredText> pages, int slot, CallbackInfo ci) {
        ItemStack stack = f_9743_.m_150109_().m_8020_(slot);
        if (stack.m_41720_() instanceof LetterItem) {
            if (!LetterItem.isSigned(stack)) {
                LetterItem.writePages(stack, pages, false);
            }
            ci.cancel();
        }
    }

    @Inject(method = "m_215208_", at = @At("HEAD"), cancellable = true, remap = false)
    private void fotfmail$signLetter(FilteredText title, List<FilteredText> pages, int slot, CallbackInfo ci) {
        ItemStack stack = f_9743_.m_150109_().m_8020_(slot);
        if (stack.m_41720_() instanceof LetterItem) {
            if (!LetterItem.isSigned(stack)) {
                stack.m_41700_("author", StringTag.m_129297_(f_9743_.m_7755_().getString()));
                stack.m_41700_("title", StringTag.m_129297_(title.f_215168_().trim()));
                LetterItem.writePages(stack, pages, true);
            }
            ci.cancel();
        }
    }
}
