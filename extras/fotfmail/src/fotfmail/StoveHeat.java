package fotfmail;

import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.tags.TagKey;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;

/**
 * Stoves heat Farmer's Delight pots and skillets whether or not they're lit (mixin/HeatableStoveMixin). Dylan,
 * 2026-11-01. Everything else stays as Farmer's Delight has it: a lit-able heat source (campfire) has to be lit.
 * The fotf:stoves tag is filled in kubejs/server_scripts/stove_heat.js from the same list that makes every stove a
 * heat source for every cooking mod.
 */
public final class StoveHeat {
    public static final TagKey<Block> STOVES = TagKey.m_203882_(Registries.f_256747_, new ResourceLocation("fotf", "stoves"));

    private StoveHeat() {
    }

    /** A heat source below a pot gives heat: always for a stove, otherwise only while it's lit (if it can be). */
    public static boolean gives(BlockState state) {
        return state.m_204336_(STOVES) || !state.m_61138_(BlockStateProperties.f_61443_)
                || state.m_61143_(BlockStateProperties.f_61443_);
    }
}
