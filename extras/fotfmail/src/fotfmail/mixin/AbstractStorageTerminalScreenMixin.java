package fotfmail.mixin;

import com.hollingsworth.arsnouveau.client.container.AbstractStorageTerminalScreen;
import com.hollingsworth.arsnouveau.client.container.SortSettings;
import com.hollingsworth.arsnouveau.client.container.StorageTerminalMenu;
import com.hollingsworth.arsnouveau.client.container.StoredItemStack;
import com.hollingsworth.arsnouveau.client.gui.buttons.StateButton;
import fotfmail.CreativeTabSort;
import fotfmail.FotfMail;
import fotfmail.LecternDeposit;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.components.Tooltip;
import net.minecraft.network.chat.Component;
import net.minecraft.client.gui.screens.inventory.AbstractContainerScreen;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * Adds "creative tab order" (CreativeTabSort, type 2) to the Storage Lectern's sort button, after amount and name.
 * - lambda$init$1 is the sort button's click: cycle through 3 modes instead of Ars's 2.
 * - onPacket restores the saved mode (the lectern saves the type number; Ars would wrap 2 back to 0).
 * - init (m_7856_) widens the button's icon sheet to 3 tiles (kubejs/assets/ars_nouveau/textures/gui/sort_type.png)
 *   and adds a "move matching items" button (LecternDeposit).
 */
@Mixin(AbstractStorageTerminalScreen.class)
public abstract class AbstractStorageTerminalScreenMixin {
    @Shadow(remap = false)
    private StoredItemStack.IStoredItemStackComparator comparator;
    @Shadow(remap = false)
    protected StateButton buttonSortingType;
    @Shadow(remap = false)
    private boolean refreshItemList;

    @Shadow(remap = false)
    protected abstract void sendUpdate();

    @Inject(method = "lambda$init$1", at = @At("HEAD"), cancellable = true, remap = false)
    private void fotfmail$cycleSortModes(Button button, CallbackInfo ci) {
        int next = (comparator.type() + 1) % (StoredItemStack.SortingTypes.VALUES.length + 1);
        boolean reversed = comparator.isReversed();
        if (next == CreativeTabSort.TYPE) {
            CreativeTabSort.reset();
            comparator = new CreativeTabSort(reversed);
        } else {
            comparator = StoredItemStack.SortingTypes.VALUES[next].create(reversed);
        }
        buttonSortingType.state = next;
        sendUpdate();
        refreshItemList = true;
        ci.cancel();
    }

    @Inject(method = "onPacket", at = @At("TAIL"), remap = false)
    private void fotfmail$restoreCreativeSort(CallbackInfo ci) {
        Object menu = ((AbstractContainerScreen<?>) (Object) this).m_6262_();
        SortSettings settings = menu instanceof StorageTerminalMenu terminal ? terminal.terminalData : null;
        if (settings != null && settings.sortType == CreativeTabSort.TYPE) {
            CreativeTabSort.reset();
            comparator = new CreativeTabSort(settings.reverseSort);
            if (buttonSortingType != null) {
                buttonSortingType.state = CreativeTabSort.TYPE;
            }
            refreshItemList = true;
        }
    }

    @Inject(method = "m_7856_", at = @At("TAIL"), remap = false)
    private void fotfmail$threeSortIcons(CallbackInfo ci) {
        // "Move matching items" (LecternDeposit), above the lectern's own buttons on the left of the panel.
        AbstractContainerScreenAccessor screen = (AbstractContainerScreenAccessor) (Object) this;
        ((ScreenAccessor) (Object) this).fotfmail$addRenderableWidget(
                Button.m_253074_(Component.m_237113_("\u2193"), button -> FotfMail.NETWORK.sendToServer(new LecternDeposit()))
                        .m_252987_(screen.fotfmail$leftPos() - 17, screen.fotfmail$topPos() - 1, 22, 12)
                        .m_257505_(Tooltip.m_257550_(Component.m_237115_("fotfmail.lectern.deposit")))
                        .m_253136_());
        if (buttonSortingType != null) {
            buttonSortingType.imageWidth = 66;
            if (comparator != null && comparator.type() == CreativeTabSort.TYPE) {
                buttonSortingType.state = CreativeTabSort.TYPE;
            }
        }
    }
}
