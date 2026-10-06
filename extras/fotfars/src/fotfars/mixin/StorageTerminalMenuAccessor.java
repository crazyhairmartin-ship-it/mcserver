package fotfars.mixin;

import com.hollingsworth.arsnouveau.client.container.StorageTerminalMenu;
import com.hollingsworth.arsnouveau.common.block.tile.StorageLecternTile;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Accessor;

/** The Storage Lectern behind an open lectern screen (protected field "te"), for LecternDeposit. */
@Mixin(StorageTerminalMenu.class)
public interface StorageTerminalMenuAccessor {
    @Accessor(value = "te", remap = false)
    StorageLecternTile fotfars$lectern();
}
