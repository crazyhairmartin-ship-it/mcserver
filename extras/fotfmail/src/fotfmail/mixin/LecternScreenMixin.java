package fotfmail.mixin;

import fotfmail.LetterItem;
import net.minecraft.client.gui.screens.inventory.BookViewScreen;
import net.minecraft.client.gui.screens.inventory.LecternScreen;
import net.minecraft.world.item.ItemStack;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Redirect;

/** A signed letter on a lectern reads like a written book (vanilla only knows books, so it showed blank). m_99044_ = bookChanged. */
@Mixin(LecternScreen.class)
public abstract class LecternScreenMixin {
    @Redirect(method = "m_99044_", remap = false, at = @At(value = "INVOKE", remap = false,
            target = "Lnet/minecraft/client/gui/screens/inventory/BookViewScreen$BookAccess;m_98308_(Lnet/minecraft/world/item/ItemStack;)Lnet/minecraft/client/gui/screens/inventory/BookViewScreen$BookAccess;"))
    private BookViewScreen.BookAccess fotfmail$readLetter(ItemStack stack) {
        if (stack.m_41720_() instanceof LetterItem && LetterItem.isSigned(stack)) {
            return new BookViewScreen.WrittenBookAccess(stack);
        }
        return BookViewScreen.BookAccess.m_98308_(stack);
    }
}
