package fotfskills.world;

import it.unimi.dsi.fastutil.longs.Long2ByteOpenHashMap;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.saveddata.SavedData;

/**
 * Irrigator: farmland a player tilled, with the player's Irrigator rank at the time. The farmland finds water that many
 * blocks further away (FarmBlockIrrigatorMixin). Saved as data/fotfskills_irrigated.dat in the dimension folder.
 */
public final class IrrigatedFarmland extends SavedData {
    private static final String NAME = "fotfskills_irrigated";
    private final Long2ByteOpenHashMap ranks = new Long2ByteOpenHashMap();

    public static IrrigatedFarmland of(ServerLevel level) {
        return level.m_8895_().m_164861_(IrrigatedFarmland::load, IrrigatedFarmland::new, NAME);
    }

    private static IrrigatedFarmland load(CompoundTag tag) {
        IrrigatedFarmland data = new IrrigatedFarmland();
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
