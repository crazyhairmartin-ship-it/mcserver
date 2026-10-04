package fotfskills.perk;

import fotfskills.world.IrrigatedFarmland;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraftforge.common.ToolActions;
import net.minecraftforge.event.level.BlockEvent;
import net.minecraftforge.eventbus.api.EventPriority;
import net.minecraftforge.eventbus.api.SubscribeEvent;

/**
 * Irrigator: farmland you till remembers your rank (the water check itself is FarmBlockIrrigatorMixin). Forge fires this
 * before the block changes, so the event still shows dirt; the mark only matters once the block is farmland.
 */
public final class IrrigatorPerks {
    @SubscribeEvent(priority = EventPriority.LOWEST)
    public void onTill(BlockEvent.BlockToolModificationEvent event) {
        if (event.isCanceled() || event.isSimulated() || event.getToolAction() != ToolActions.HOE_TILL
                || !(event.getPlayer() instanceof ServerPlayer player) || !(event.getLevel() instanceof ServerLevel level)) {
            return;
        }
        IrrigatedFarmland.of(level).set(event.getPos(), (int) Math.round(Perks.get(player, "irrigator")));
    }
}
