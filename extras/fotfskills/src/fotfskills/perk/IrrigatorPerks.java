package fotfskills.perk;

import fotfskills.world.IrrigatedFarmland;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.level.block.FarmBlock;
import net.minecraftforge.common.ToolActions;
import net.minecraftforge.event.level.BlockEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;

/** Irrigator: farmland you till remembers your rank (the water check itself is FarmBlockIrrigatorMixin). */
public final class IrrigatorPerks {
    @SubscribeEvent(priority = EventPriority.LOWEST)
    public void onTill(BlockEvent.BlockToolModificationEvent event) {
        if (event.isCanceled() || event.isSimulated() || event.getToolAction() != ToolActions.HOE_TILL
                || !(event.getPlayer() instanceof ServerPlayer player) || !(event.getLevel() instanceof ServerLevel level)
                || event.getFinalState() == null || !(event.getFinalState().m_60734_() instanceof FarmBlock)) {
            return;
        }
        IrrigatedFarmland.of(level).set(event.getPos(), (int) Math.round(Perks.get(player, "irrigator")));
    }
}
