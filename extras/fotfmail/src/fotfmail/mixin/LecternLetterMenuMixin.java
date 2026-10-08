package fotfmail.mixin;

import fotfmail.LetterItem;
import net.minecraft.world.Container;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.inventory.AbstractContainerMenu;
import net.minecraft.world.inventory.ContainerData;
import net.minecraft.world.inventory.LecternMenu;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.entity.LecternBlockEntity;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * A signed letter on a lectern opens the normal reading menu. Amendments swaps in its "edit the book and quill on the
 * lectern" menu for anything that is a WritableBookItem, letters included, which showed the letter's raw page text with
 * Sign / Done buttons. Priority 500 runs this before Amendments' own createMenu hook. m_7208_ = createMenu,
 * f_59525_ = bookAccess, f_59526_ = dataAccess, m_59566_ = getBook.
 */
@Mixin(value = LecternBlockEntity.class, priority = 500)
public abstract class LecternLetterMenuMixin {
    @Shadow(remap = false)
    @Final
    private Container f_59525_;
    @Shadow(remap = false)
    @Final
    private ContainerData f_59526_;

    @Shadow(remap = false)
    public abstract ItemStack m_59566_();

    @Inject(method = "m_7208_", at = @At("HEAD"), cancellable = true, remap = false)
    private void fotfmail$readLetter(int id, Inventory inventory, Player player, CallbackInfoReturnable<AbstractContainerMenu> cir) {
        ItemStack book = m_59566_();
        if (book.m_41720_() instanceof LetterItem && LetterItem.isSigned(book)) {
            cir.setReturnValue(new LecternMenu(id, f_59525_, f_59526_));
        }
    }
}
