package fotfskills.compat;

import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.tags.TagKey;
import net.minecraft.world.level.block.state.BlockState;

/**
 * World checks the quest scripts (kubejs/server_scripts/quest_npcs.js) can't do from KubeJS: whether a spot is inside
 * a structure (escorts, holding a spot, timed goals that reach a structure) and counting blocks around a spot (build
 * tasks). Called as Java.loadClass('fotfskills.compat.QuestWorld').
 */
public final class QuestWorld {
    private QuestWorld() {}

    /** Is (x, y, z) inside a structure with this id, or "#namespace:tag"? */
    public static boolean inStructure(ServerLevel level, double x, double y, double z, String structure) {
        return QuestProtectHooks.inStructure(level, BlockPos.m_274561_(x, y, z), structure);
    }

    /**
     * How many blocks of each key ("namespace:id" or "#namespace:tag") are within radius of (x, y, z): one count per
     * key, in order. Radius is capped at 12 (a 25-block cube).
     */
    public static int[] countBlocks(ServerLevel level, double x, double y, double z, int radius, List<String> keys) {
        int r = Math.max(0, Math.min(12, radius));
        int[] counts = new int[keys.size()];
        BlockPos centre = BlockPos.m_274561_(x, y, z);
        for (BlockPos pos : BlockPos.m_121940_(centre.m_7918_(-r, -r, -r), centre.m_7918_(r, r, r))) {
            BlockState state = level.m_8055_(pos);
            if (state.m_60795_()) {
                continue;
            }
            String id = BuiltInRegistries.f_256975_.m_7981_(state.m_60734_()).toString();
            for (int i = 0; i < counts.length; i++) {
                String key = keys.get(i);
                if (key.startsWith("#")) {
                    ResourceLocation rl = ResourceLocation.m_135820_(key.substring(1));
                    if (rl != null && state.m_204336_(TagKey.m_203882_(Registries.f_256747_, rl))) {
                        counts[i]++;
                    }
                } else if (key.equals(id)) {
                    counts[i]++;
                }
            }
        }
        return counts;
    }
}
