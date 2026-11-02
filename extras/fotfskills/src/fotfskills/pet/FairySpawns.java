package fotfskills.pet;

import java.util.List;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.SpawnPlacements;
import net.minecraft.world.entity.animal.Animal;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraftforge.event.entity.SpawnPlacementRegisterEvent;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.registries.ForgeRegistries;

/**
 * Fay's Fairies spawn by the monster rule (dark enough for a hostile mob), left over from registering them as
 * monsters. FairyCategoryMixin made them creatures, so they're only tried in animal spawning, where that darkness
 * check almost never passes: nobody had seen one, even in the Twilight Forest (Dylan, 2026-11-02). They use the
 * animal rule instead: on grass, in daylight-level light, like cows and sheep. Where they spawn is still set by the
 * fotf fairy biome modifiers.
 */
public final class FairySpawns {
    private static final List<String> FAIRIES = List.of("blue_fairy", "gold_fairy", "pink_fairy");

    private FairySpawns() {
    }

    public static void register(IEventBus modBus) {
        modBus.addListener(FairySpawns::onSpawnPlacements);
    }

    @SuppressWarnings("unchecked")
    private static void onSpawnPlacements(SpawnPlacementRegisterEvent event) {
        for (String id : FAIRIES) {
            EntityType<?> type = ForgeRegistries.ENTITY_TYPES.getValue(new ResourceLocation("fays_fairies", id));
            if (type == null) {
                continue;
            }
            event.register((EntityType<Animal>) type, SpawnPlacements.Type.ON_GROUND,
                    Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, Animal::m_218104_,
                    SpawnPlacementRegisterEvent.Operation.REPLACE);
        }
    }
}
