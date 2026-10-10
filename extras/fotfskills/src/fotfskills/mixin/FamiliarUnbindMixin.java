package fotfskills.mixin;

import net.fayebeard.bookffamiliars.data.FamiliarBookData;
import net.fayebeard.bookffamiliars.data.StoredFamiliar;
import net.fayebeard.bookffamiliars.network.DeleteFamiliarPacket;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraftforge.network.NetworkEvent;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.Redirect;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * Book of Familiars' Delete becomes Unbind for a familiar stored in the book: it's let out beside its owner (still
 * tamed to them) instead of vanishing with the page. Recovering (dead) familiars have nothing to let out and are just
 * forgotten as before. Released familiars: FamiliarUnbindTrackedMixin. Labels: kubejs/assets/bookoffamiliars/lang.
 */
@Mixin(value = DeleteFamiliarPacket.class, remap = false)
public abstract class FamiliarUnbindMixin {
    private static ServerPlayer fotfskills$sender;

    @Inject(method = "lambda$handle$2", remap = false, at = @At("HEAD"))
    private static void fotfskills$sender(NetworkEvent.Context context, DeleteFamiliarPacket packet, CallbackInfo ci) {
        fotfskills$sender = context.getSender();
    }

    @Redirect(method = "lambda$handle$2", remap = false, at = @At(value = "INVOKE",
            target = "Lnet/fayebeard/bookffamiliars/data/FamiliarBookData;removeFamiliar(I)V"))
    private static void fotfskills$unbind(FamiliarBookData data, int index) {
        ServerPlayer player = fotfskills$sender;
        fotfskills$sender = null;
        if (player == null || index < 0 || index >= data.getFamiliars().size()) {
            data.removeFamiliar(index);
            return;
        }
        StoredFamiliar familiar = data.getFamiliars().get(index);
        Entity entity = EntityType.m_20645_(familiar.nbt().m_6426_(), player.m_284548_(), e -> e);
        if (entity == null) {
            data.removeFamiliar(index);                     // its mod is gone: nothing to let out
            return;
        }
        entity.m_7678_(player.m_20185_(), player.m_20186_(), player.m_20189_(), player.m_146908_(), 0);
        if (!entity.m_8077_()) entity.m_20340_(false);     // the book's floating label goes with the bond
        if (!player.m_284548_().m_7967_(entity)) {
            player.m_213846_(Component.m_237113_("Couldn't let " + familiar.displayName() + " out here; they stay in your book."));
            return;                                         // keep the page rather than lose the familiar
        }
        data.removeFamiliar(index);
    }
}
