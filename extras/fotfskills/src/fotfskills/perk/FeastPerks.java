package fotfskills.perk;

import java.util.ArrayList;
import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.IntegerProperty;
import net.minecraft.world.level.block.state.properties.Property;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.entity.player.PlayerInteractEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;

/**
 * Feast Maker: taking a serving from a feast, pie or cake (any block with a "servings" or "bites" property: Farmer's
 * Delight feasts and pies, Let's Do cakes, vanilla cake) has a chance to leave the block as it was, so the slice is free.
 * Checked at the end of the tick the player right-clicked, once the block has handed out its serving.
 */
public final class FeastPerks {
    private record Take(ServerPlayer player, ServerLevel level, BlockPos pos, BlockState before) {
    }

    private final List<Take> pending = new ArrayList<>();

    @SubscribeEvent
    public void onUse(PlayerInteractEvent.RightClickBlock event) {
        if (event.getEntity() instanceof ServerPlayer player && event.getLevel() instanceof ServerLevel level
                && Perks.get(player, "feast_maker") > 0) {
            pending.add(new Take(player, level, event.getPos().m_7949_(), level.m_8055_(event.getPos())));
        }
    }

    @SubscribeEvent
    public void onServerTick(TickEvent.ServerTickEvent event) {
        if (event.phase != TickEvent.Phase.END || pending.isEmpty()) {
            return;
        }
        for (Take take : pending) {
            BlockState after = take.level.m_8055_(take.pos);
            if (after.m_60734_() != take.before.m_60734_()) {
                continue;                              // last slice eaten or block replaced: nothing to give back
            }
            for (Property<?> property : take.before.m_61147_()) {
                if (property instanceof IntegerProperty ints
                        && ServingRule.taken(ints.m_61708_(), take.before.m_61143_(ints), after.m_61143_(ints))
                        && Perks.roll(take.player, "feast_maker")) {
                    take.level.m_7731_(take.pos, take.before, 3);
                    break;
                }
            }
        }
        pending.clear();
    }
}
