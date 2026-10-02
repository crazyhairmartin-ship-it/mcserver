package fotfmail.mixin;

import fotfmail.LetterViewScreen;
import net.minecraft.client.gui.screens.inventory.BookViewScreen;
import net.minecraft.resources.ResourceLocation;
import org.objectweb.asm.Opcodes;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Redirect;

/** Reading a letter (LetterViewScreen) draws letter paper instead of the book page. f_98252_ = BOOK_LOCATION. */
@Mixin(BookViewScreen.class)
public abstract class BookViewScreenMixin {
    @Shadow(remap = false)
    @Final
    public static ResourceLocation f_98252_;

    @Redirect(method = "m_88315_", remap = false, at = @At(value = "FIELD", opcode = Opcodes.GETSTATIC, remap = false,
            target = "Lnet/minecraft/client/gui/screens/inventory/BookViewScreen;f_98252_:Lnet/minecraft/resources/ResourceLocation;"))
    private ResourceLocation fotfmail$letterPaper() {
        return (Object) this instanceof LetterViewScreen ? LetterViewScreen.PAPER : f_98252_;
    }
}
