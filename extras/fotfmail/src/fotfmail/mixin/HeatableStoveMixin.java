package fotfmail.mixin;

import fotfmail.StoveHeat;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import org.spongepowered.asm.mixin.Mixin;
import vectorwing.farmersdelight.common.block.entity.CookingPotBlockEntity;
import vectorwing.farmersdelight.common.block.entity.HeatableBlockEntity;
import vectorwing.farmersdelight.common.block.entity.SkilletBlockEntity;
import vectorwing.farmersdelight.common.tag.ModTags;

/**
 * Farmer's Delight's heat check (HeatableBlockEntity.isHeated, an interface default) with one change: a stove gives
 * heat even when it isn't lit (StoveHeat). Both heatable block entities use the default, so this adds the method to
 * each and the default stops applying. Otherwise it's the same: the heat source directly below, or under a heat
 * conductor (hopper) for blocks that don't need direct heat.
 */
@Mixin(value = {CookingPotBlockEntity.class, SkilletBlockEntity.class}, remap = false)
public abstract class HeatableStoveMixin implements HeatableBlockEntity {
    @Override
    public boolean isHeated(Level level, BlockPos pos) {
        BlockState below = level.m_8055_(pos.m_7495_());
        if (below.m_204336_(ModTags.Blocks.HEAT_SOURCES)) {
            return StoveHeat.gives(below);
        }
        if (!requiresDirectHeat() && below.m_204336_(ModTags.Blocks.HEAT_CONDUCTORS)) {
            BlockState source = level.m_8055_(pos.m_6625_(2));
            return source.m_204336_(ModTags.Blocks.HEAT_SOURCES) && StoveHeat.gives(source);
        }
        return false;
    }
}
