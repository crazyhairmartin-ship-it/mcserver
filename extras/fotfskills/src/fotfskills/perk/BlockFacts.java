package fotfskills.perk;

import fotfskills.xp.BreakRules;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.tags.TagKey;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.CropBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.IntegerProperty;
import net.minecraft.world.level.block.state.properties.Property;
import net.minecraftforge.registries.ForgeRegistries;

/** What the break rules and block perks need to know about a block state. */
public record BlockFacts(BlockState state) implements BreakRules.Facts {
    private static final Map<String, TagKey<Block>> TAGS = new ConcurrentHashMap<>();

    @Override
    public String id() {
        ResourceLocation key = ForgeRegistries.BLOCKS.getKey(state.m_60734_());
        return key == null ? "" : key.toString();
    }

    @Override
    public boolean hasTag(String tag) {
        return state.m_204336_(TAGS.computeIfAbsent(tag, t -> TagKey.m_203882_(ForgeRegistries.Keys.BLOCKS, new ResourceLocation(t))));
    }

    /** Fully grown: CropBlock.isMaxAge, or an "age" property at its maximum for other blocks in #minecraft:crops. */
    @Override
    public boolean matureCrop() {
        if (state.m_60734_() instanceof CropBlock crop) {
            return crop.m_52307_(state);
        }
        if (!hasTag("minecraft:crops")) {
            return false;
        }
        for (Property<?> property : state.m_61147_()) {
            if (property instanceof IntegerProperty age && age.m_61708_().equals("age")) {
                int max = age.m_6908_().stream().max(Integer::compare).orElse(0);
                return state.m_61143_(age) == max;
            }
        }
        return false;
    }
}
