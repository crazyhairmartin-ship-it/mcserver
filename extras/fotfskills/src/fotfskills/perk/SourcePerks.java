package fotfskills.perk;

import fotfskills.world.RankedBlocks;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraftforge.event.level.BlockEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;

/**
 * Sourcecraft: an Ars Nouveau sourcelink remembers its placer's rank (10% more source per rank, applied by
 * ArsSourcelinkMixin). The cheaper enchanting apparatus half is ArsApparatusMixin.
 */
public final class SourcePerks {
    @SubscribeEvent(priority = EventPriority.LOWEST)
    public void onPlace(BlockEvent.EntityPlaceEvent event) {
        if (event.isCanceled() || !(event.getEntity() instanceof ServerPlayer player)
                || !(event.getLevel() instanceof ServerLevel level)) {
            return;
        }
        BlockEntity placed = level.m_7702_(event.getPos());
        if (placed != null && isSourcelink(placed.getClass())) {
            RankedBlocks.of(level, RankedBlocks.SOURCELINKS).set(event.getPos(), (int) Math.round(Perks.get(player, "source_gain") * 10));
        }
    }

    static boolean isSourcelink(Class<?> type) {
        for (Class<?> c = type; c != null; c = c.getSuperclass()) {
            if (c.getName().equals("com.hollingsworth.arsnouveau.common.block.tile.SourcelinkTile")) {
                return true;
            }
        }
        return false;
    }
}
