package fotfmail.mixin;

import fotfmail.LetterItem;
import net.minecraft.client.gui.screens.inventory.BookEditScreen;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.ItemStack;
import org.objectweb.asm.Opcodes;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Redirect;

/**
 * When signing a Letter, the book screen asks for the recipient instead of a book title, and its "can't edit
 * after signing" note talks about sealing the letter. Normal books are unchanged.
 * f_98060_ = EDIT_TITLE_LABEL ("Enter Book Title:"), f_98061_ = FINALIZE_WARNING_LABEL, f_98065_ = the book stack,
 * m_88315_ = render.
 */
@Mixin(BookEditScreen.class)
public abstract class BookEditScreenMixin {
    private static final Component FOTFMAIL_RECIPIENT = Component.m_237115_("fotfmail.letter.recipient");
    private static final Component FOTFMAIL_SEAL_WARNING = Component.m_237115_("fotfmail.letter.seal_warning");

    @Shadow(remap = false)
    @Final
    private static Component f_98060_;
    @Shadow(remap = false)
    @Final
    private static Component f_98061_;
    @Shadow(remap = false)
    @Final
    private ItemStack f_98065_;

    @Redirect(method = "m_88315_", remap = false, at = @At(value = "FIELD", opcode = Opcodes.GETSTATIC, remap = false,
            target = "Lnet/minecraft/client/gui/screens/inventory/BookEditScreen;f_98060_:Lnet/minecraft/network/chat/Component;"))
    private Component fotfmail$recipientLabel() {
        return f_98065_.m_41720_() instanceof LetterItem ? FOTFMAIL_RECIPIENT : f_98060_;
    }

    @Redirect(method = "m_88315_", remap = false, at = @At(value = "FIELD", opcode = Opcodes.GETSTATIC, remap = false,
            target = "Lnet/minecraft/client/gui/screens/inventory/BookEditScreen;f_98061_:Lnet/minecraft/network/chat/Component;"))
    private Component fotfmail$sealWarning() {
        return f_98065_.m_41720_() instanceof LetterItem ? FOTFMAIL_SEAL_WARNING : f_98061_;
    }
}
