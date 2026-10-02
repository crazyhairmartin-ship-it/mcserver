package fotfmail;

import net.minecraft.client.gui.screens.inventory.BookViewScreen;
import net.minecraft.resources.ResourceLocation;

/** Reading a signed letter: the book view, drawn on letter paper (BookViewScreenMixin checks for this class). */
public final class LetterViewScreen extends BookViewScreen {
    public static final ResourceLocation PAPER = new ResourceLocation(FotfMail.MODID, "textures/gui/letter.png");

    public LetterViewScreen(BookAccess access) {
        super(access);
    }
}
