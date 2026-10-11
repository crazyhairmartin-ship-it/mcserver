package fotfskills.mixin;

import fotfskills.compat.OreScentOutline;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraftforge.registries.ForgeRegistries;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;

/**
 * Ore Scenting's ore outline (the highlighted block always glows, so the glow takes the entity's team colour) is
 * coloured by the ore inside: compat/OreScentOutline.colour.
 */
@Mixin(targets = "com.github.alexthe668.domesticationinnovation.server.entity.HighlightedBlockEntity", remap = false)
public abstract class OreScentColourMixin extends Entity {
    private OreScentColourMixin(EntityType<?> type, Level level) {
        super(type, level);
    }

    @Shadow(remap = false)
    public abstract BlockState getBlockState();

    @Override
    public int m_19876_() {
        var key = ForgeRegistries.BLOCKS.getKey(getBlockState().m_60734_());
        return key == null ? 0xFFFFFF : OreScentOutline.colour(key.toString());
    }
}
