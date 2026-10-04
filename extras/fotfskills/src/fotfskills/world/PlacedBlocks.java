package fotfskills.world;

import fotfskills.perk.BlockFacts;
import java.util.ArrayList;
import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.saveddata.SavedData;

/**
 * Positions of player-placed gathering blocks (ores, logs, stone, flowers, mushrooms) in one dimension, so
 * re-mining them gives no skill XP or extra drops. Marks follow blocks pushed by pistons. Saved as
 * data/fotfskills_placed.dat in the dimension folder.
 */
public final class PlacedBlocks extends SavedData {
    private static final String NAME = "fotfskills_placed";
    private final Marks marks = new Marks();

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
            data.marks.mark(pos);
        }
        return data;
    }

    @Override
    public CompoundTag m_7176_(CompoundTag tag) {
        tag.m_128388_("positions", marks.toArray());
        return tag;
    }

    public void mark(BlockPos pos) {
        if (marks.mark(pos.m_121878_())) {
            m_77762_();
        }
    }

    /** Forgets the position; true if it was player-placed. */
    public boolean remove(BlockPos pos) {
        boolean was = marks.remove(pos.m_121878_());
        if (was) {
            m_77762_();
        }
        return was;
    }

    /** A piston pushes these blocks one step in direction; their marks go with them. */
    public void move(List<BlockPos> pushed, Direction direction) {
        List<Long> from = new ArrayList<>();
        List<Long> to = new ArrayList<>();
        for (BlockPos pos : pushed) {
            from.add(pos.m_121878_());
            to.add(pos.m_121945_(direction).m_121878_());
        }
        if (marks.move(from, to)) {
            m_77762_();
        }
    }
}
