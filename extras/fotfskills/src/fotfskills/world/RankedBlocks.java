package fotfskills.world;

import it.unimi.dsi.fastutil.longs.Long2ByteOpenHashMap;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.saveddata.SavedData;

/**
 * Blocks a player placed or worked, with their perk rank at the time, one set per use (saved as data/<name>.dat in the
 * dimension folder): IRRIGATED farmland (Irrigator) and SOURCELINKS (Sourcecraft).
 */
public final class RankedBlocks extends SavedData {
    public static final String IRRIGATED = "fotfskills_irrigated";
    public static final String SOURCELINKS = "fotfskills_sourcelinks";
    private final Long2ByteOpenHashMap ranks = new Long2ByteOpenHashMap();

    public static RankedBlocks of(ServerLevel level, String name) {
        return level.m_8895_().m_164861_(RankedBlocks::load, RankedBlocks::new, name);
    }

    private static RankedBlocks load(CompoundTag tag) {
        RankedBlocks data = new RankedBlocks();
        long[] positions = tag.m_128467_("positions");
        byte[] ranks = tag.m_128463_("ranks");
        for (int i = 0; i < Math.min(positions.length, ranks.length); i++) {
            data.ranks.put(positions[i], ranks[i]);
        }
        return data;
    }

    @Override
    public CompoundTag m_7176_(CompoundTag tag) {
        tag.m_128388_("positions", ranks.keySet().toLongArray());
        byte[] values = new byte[ranks.size()];
        int i = 0;
        for (long pos : ranks.keySet().toLongArray()) {
            values[i++] = ranks.get(pos);
        }
        tag.m_128382_("ranks", values);
        return tag;
    }

    public int rank(BlockPos pos) {
        return ranks.get(pos.m_121878_());
    }

    public void set(BlockPos pos, int rank) {
        long key = pos.m_121878_();
        if (rank <= 0 ? ranks.remove(key) != 0 : ranks.put(key, (byte) rank) != rank) {
            m_77762_();
        }
    }
}
