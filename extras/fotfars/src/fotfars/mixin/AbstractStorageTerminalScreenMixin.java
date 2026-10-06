package fotfars.mixin;

import com.hollingsworth.arsnouveau.client.container.AbstractStorageTerminalScreen;
import com.hollingsworth.arsnouveau.client.container.SortSettings;
import com.hollingsworth.arsnouveau.client.container.StorageTerminalMenu;
import com.hollingsworth.arsnouveau.client.container.StoredItemStack;
import com.hollingsworth.arsnouveau.client.gui.buttons.StateButton;
import com.hollingsworth.arsnouveau.client.gui.buttons.StorageSettingsButton;
import fotfars.CreativeTabSort;
import fotfars.FotfArs;
import fotfars.LecternDeposit;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.components.Tooltip;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
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
 *   and adds "restock" and "move matching items" tabs (LecternDeposit).
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
    private void fotfars$cycleSortModes(Button button, CallbackInfo ci) {
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
    private void fotfars$restoreCreativeSort(CallbackInfo ci) {
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
    private void fotfars$threeSortIcons(CallbackInfo ci) {
        // "Restock" and "move matching items" (LecternDeposit) as purple side tabs like the lectern's own, stacked
        // above them (Ars's sit at topPos + 14, 29, 44).
        fotfars$addTab(-16, "lectern_restock", "fotfars.lectern.restock", true);
        fotfars$addTab(-1, "lectern_deposit", "fotfars.lectern.deposit", false);
        if (buttonSortingType != null) {
            buttonSortingType.imageWidth = 66;
            if (comparator != null && comparator.type() == CreativeTabSort.TYPE) {
                buttonSortingType.state = CreativeTabSort.TYPE;
            }
        }
    }

    private void fotfars$addTab(int y, String icon, String tooltip, boolean restock) {
        AbstractContainerScreenAccessor screen = (AbstractContainerScreenAccessor) (Object) this;
        StorageSettingsButton tab = new StorageSettingsButton(screen.fotfars$leftPos() - 17, screen.fotfars$topPos() + y,
                22, 12, 22, 13, 0, new ResourceLocation(FotfArs.MODID, "textures/gui/" + icon + ".png"),
                button -> FotfArs.NETWORK.sendToServer(new LecternDeposit(restock)));
        tab.m_257544_(Tooltip.m_257550_(Component.m_237115_(tooltip)));
        ((ScreenAccessor) (Object) this).fotfars$addRenderableWidget(tab);
    }
}
