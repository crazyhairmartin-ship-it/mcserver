package fotfmail.mixin;

import com.obscura.storage.Config;
import com.obscura.storage.block.IInventoryCable;
import com.obscura.storage.block.InventoryConnectorBlock;
import com.obscura.storage.tile.InventoryConnectorBlockEntity;
import com.obscura.storage.tile.InventoryInterfaceBlockEntity;
import java.util.ArrayDeque;
import java.util.HashSet;
import java.util.Set;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraftforge.items.IItemHandler;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * Obscura's Inventory Interface finds its network by walking Inventory Cable to an Inventory Connector, but its walk
 * marks blocks as seen when it first looks at them and only looks around the blocks a cable points to, so depending
 * on where it starts it can pass right next to the connector without checking it: the smelter interface found
 * nothing while the farm interface on the same cable found the connector (Dylan, 2026-11-02). This walks every
 * connected cable (the mod's own IInventoryCable.next) and checks all six sides of each for a connector. If it finds
 * none, the mod's own search still runs.
 */
@Mixin(value = InventoryInterfaceBlockEntity.class, remap = false)
public abstract class InterfaceSearchMixin {
    @Inject(method = "findConnectorInventory", at = @At("HEAD"), cancellable = true, remap = false, require = 0)
    private void fotfmail$findOverAllCable(CallbackInfoReturnable<IItemHandler> cir) {
        BlockEntity self = (BlockEntity) (Object) this;
        Level level = self.m_58904_();
        if (level == null) {
            return;
        }
        IItemHandler found = fotfmail$search(level, self.m_58899_(), Config.get().invConnectorMaxCables);
        if (found != null) {
            cir.setReturnValue(found);
        }
    }

    private static IItemHandler fotfmail$search(Level level, BlockPos start, int maxCables) {
        ArrayDeque<BlockPos> queue = new ArrayDeque<>();
        Set<BlockPos> cables = new HashSet<>();
        queue.add(start);
        cables.add(start);
        while (!queue.isEmpty() && cables.size() <= maxCables) {
            BlockPos pos = queue.poll();
            for (Direction dir : Direction.values()) {
                BlockPos side = pos.m_121945_(dir);
                if (!level.m_46749_(side)) {
                    continue;
                }
                BlockState state = level.m_8055_(side);
                if (state.m_60734_() instanceof InventoryConnectorBlock
                        && level.m_7702_(side) instanceof InventoryConnectorBlockEntity connector) {
                    return connector.getInventory();
                }
            }
            BlockState here = level.m_8055_(pos);
            if (pos != start && !(here.m_60734_() instanceof IInventoryCable)) {
                continue;
            }
            for (Direction dir : Direction.values()) {
                BlockPos side = pos.m_121945_(dir);
                if (cables.contains(side) || !level.m_46749_(side)) {
                    continue;
                }
                BlockState state = level.m_8055_(side);
                if (state.m_60734_() instanceof IInventoryCable cable && fotfmail$joins(cable, level, state, side, pos)) {
                    cables.add(side);
                    queue.add(side);
                }
            }
        }
        return null;
    }

    /** Whether the cable at side connects back towards from (the mod's own connection rule), or is plain adjacency. */
    private static boolean fotfmail$joins(IInventoryCable cable, Level level, BlockState state, BlockPos side, BlockPos from) {
        java.util.List<BlockPos> next = cable.next(level, state, side);
        return next == null || next.isEmpty() || next.contains(from);
    }
}
