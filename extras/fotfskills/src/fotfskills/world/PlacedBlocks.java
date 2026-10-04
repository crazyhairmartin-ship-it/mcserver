package fotfskills.world;

import fotfskills.perk.BlockFacts;
import it.unimi.dsi.fastutil.longs.LongOpenHashSet;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.saveddata.SavedData;

/**
 * Positions of player-placed gathering blocks (ores, logs, stone, flowers, mushrooms) in one dimension, so
 * re-mining them gives no skill XP or extra drops. Saved as data/fotfskills_placed.dat in the dimension folder.
 */
public final class PlacedBlocks extends SavedData {
    private static final String NAME = "fotfskills_placed";
    private final LongOpenHashSet positions = new LongOpenHashSet();

    public static PlacedBlocks of(ServerLevel level) {
        return level.m_8895_().m_164861_(PlacedBlocks::load, PlacedBlocks::new, NAME);
    }

    public static boolean tracked(BlockFacts facts) {
        return facts.hasTag("forge:ores") || facts.hasTag("minecraft:logs")
                || facts.hasTag("minecraft:base_stone_overworld") || facts.hasTag("minecraft:base_stone_nether")
                || facts.hasTag("minecraft:flowers") || facts.id().endsWith("_mushroom");
    }

    private static PlacedBlocks load(CompoundTag tag) {
        PlacedBlocks data = new PlacedBlocks();
        for (long pos : tag.m_128467_("positions")) {
            data.positions.add(pos);
        }
        return data;
    }

    @Override
    public CompoundTag m_7176_(CompoundTag tag) {
        tag.m_128388_("positions", positions.toLongArray());
        return tag;
    }

    public void mark(BlockPos pos) {
        if (positions.add(pos.m_121878_())) {
            m_77762_();
        }
    }

    /** Forgets the position; true if it was player-placed. */
    public boolean remove(BlockPos pos) {
        boolean was = positions.remove(pos.m_121878_());
        if (was) {
            m_77762_();
        }
        return was;
    }
}
