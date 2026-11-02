package fotfmail.mixin;

import com.obscura.storage.tile.InventoryConnectorBlockEntity;
import java.util.List;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Accessor;

/** InventoryConnectorBlockEntity.linkedInvs is private; CableConnectorRelinkMixin checks it. */
@Mixin(value = InventoryConnectorBlockEntity.class, remap = false)
public interface InventoryConnectorAccessor {
    @Accessor(value = "linkedInvs", remap = false)
    List<InventoryConnectorBlockEntity.LinkedInv> fotfmail$linkedInvs();
}
