package fotfmail.mixin;

import fotfmail.LetterItem;
import net.minecraft.world.level.block.entity.LecternBlockEntity;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * A lectern holding a letter has a book: vanilla's hasBook (m_59567_) only knows book and quill / written book, so the
 * reading screen closed the moment it opened (the menu checks hasBook every tick). m_59566_ = getBook.
 */
@Mixin(LecternBlockEntity.class)
public abstract class LecternBlockEntityMixin {
    @Inject(method = "m_59567_", at = @At("HEAD"), cancellable = true, remap = false)
    private void fotfmail$letterIsABook(CallbackInfoReturnable<Boolean> cir) {
        if (((LecternBlockEntity) (Object) this).m_59566_().m_41720_() instanceof LetterItem) {
            cir.setReturnValue(true);
        }
    }
}
