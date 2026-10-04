package fotfskills.perk;

import net.minecraft.resources.ResourceLocation;
import net.minecraft.tags.TagKey;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.level.biome.Biome;
import net.minecraftforge.registries.ForgeRegistries;

/** Biome checks shared by perks (Druid's Grove; ConditionalStats has its own forest check for Forest Stride). */
public final class Biomes {
    private static TagKey<Biome> forest;

    private Biomes() {
    }

    public static boolean inForest(LivingEntity entity) {
        if (forest == null) {
            forest = TagKey.m_203882_(ForgeRegistries.Keys.BIOMES, new ResourceLocation("minecraft", "is_forest"));
        }
        return entity.m_9236_().m_204166_(entity.m_20183_()).m_203656_(forest);
    }
}
