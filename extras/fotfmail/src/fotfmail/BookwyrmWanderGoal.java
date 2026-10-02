package fotfmail;

import com.hollingsworth.arsnouveau.common.block.tile.StorageLecternTile;
import com.hollingsworth.arsnouveau.common.entity.EntityBookwyrm;
import java.util.ArrayList;
import java.util.EnumSet;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import net.minecraft.core.BlockPos;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.pathfinder.Path;
import net.minecraft.world.level.block.entity.BlockEntity;

/**
 * Bookwyrms (Ars Nouveau) only move to transfer items or to hover at a random linked chest, so idle ones just sit
 * by the chests. This makes them flutter around their lectern network now and then: sometimes hovering over one of
 * the connected lecterns (their own, plus any lecterns linked to it, following chains), otherwise flying to an
 * open spot within RADIUS blocks of one of them. Only spots they can actually fly to are picked (lecterns on another
 * floor need an opening between). Same priority as their chest visits, below transfers, so work always comes first.
 */
public final class BookwyrmWanderGoal extends Goal {
    private static final int RADIUS = 8;
    private static final int CHANCE = 20; // ~1 in 20 checks while idle
    private static final int LECTERN_VISIT_CHANCE = 3; // 1 in 3 wanders hover over a lectern
    private static final int MAX_TICKS = 160;
    private static final long NETWORK_REFRESH_TICKS = 1200; // re-scan linked lecterns once a minute
    private static final int LINK_RANGE_CHUNKS = 2; // Ars links lecterns within 30 blocks
    private final EntityBookwyrm bookwyrm;
    private int ticks;
    private List<BlockPos> network = List.of();
    private long networkScannedAt = Long.MIN_VALUE;

    public BookwyrmWanderGoal(EntityBookwyrm bookwyrm) {
        this.bookwyrm = bookwyrm;
        m_7021_(EnumSet.of(Goal.Flag.MOVE));
    }

    @Override
    public boolean m_8036_() {
        return bookwyrm.m_217043_().m_188503_(CHANCE) == 0;
    }

    @Override
    public void m_8056_() {
        ticks = 0;
        List<BlockPos> lecterns = lecternNetwork();
        BlockPos home = lecterns.isEmpty() ? bookwyrm.m_20183_() : lecterns.get(bookwyrm.m_217043_().m_188503_(lecterns.size()));
        Level level = bookwyrm.m_9236_();
        if (!lecterns.isEmpty() && bookwyrm.m_217043_().m_188503_(LECTERN_VISIT_CHANCE) == 0
                && level.m_46859_(home.m_7494_()) && flyTo(home.m_7494_())) {
            return;
        }
        for (int attempt = 0; attempt < 10; attempt++) {
            BlockPos spot = home.m_7918_(
                    bookwyrm.m_217043_().m_188503_(RADIUS * 2 + 1) - RADIUS,
                    bookwyrm.m_217043_().m_188503_(5) - 1,
                    bookwyrm.m_217043_().m_188503_(RADIUS * 2 + 1) - RADIUS);
            if (level.m_46859_(spot) && level.m_46859_(spot.m_7494_()) && flyTo(spot)) {
                return;
            }
        }
    }

    /** Starts flying to pos if there's a full path there; false if it can't be reached (e.g. through a floor). */
    private boolean flyTo(BlockPos pos) {
        Path path = bookwyrm.m_21573_().m_7864_(pos, 0);
        return path != null && path.m_77403_() && bookwyrm.m_21573_().m_26536_(path, 1.0);
    }

    /** The bookwyrm's own lectern plus every loaded lectern linked to it (directly or through other lecterns). */
    private List<BlockPos> lecternNetwork() {
        Level level = bookwyrm.m_9236_();
        long now = level.m_46467_();
        BlockPos main = bookwyrm.lecternPos;
        if (main == null) {
            return List.of();
        }
        if (now - networkScannedAt < NETWORK_REFRESH_TICKS && !network.isEmpty()) {
            return network;
        }
        List<StorageLecternTile> nearby = new ArrayList<>();
        int cx = main.m_123341_() >> 4;
        int cz = main.m_123343_() >> 4;
        int range = LINK_RANGE_CHUNKS * 3; // chains can reach further than one hop
        for (int x = cx - range; x <= cx + range; x++) {
            for (int z = cz - range; z <= cz + range; z++) {
                if (!level.m_7232_(x, z)) {
                    continue;
                }
                for (BlockEntity blockEntity : level.m_6325_(x, z).m_62954_().values()) {
                    if (blockEntity instanceof StorageLecternTile lectern) {
                        nearby.add(lectern);
                    }
                }
            }
        }
        Set<BlockPos> found = new HashSet<>();
        found.add(main);
        boolean grew = true;
        while (grew) {
            grew = false;
            for (StorageLecternTile lectern : nearby) {
                BlockPos pos = lectern.m_58899_();
                if (lectern.mainLecternPos != null && found.contains(lectern.mainLecternPos) && found.add(pos)) {
                    grew = true;
                }
            }
        }
        network = new ArrayList<>(found);
        networkScannedAt = now;
        return network;
    }

    @Override
    public boolean m_8045_() {
        return ++ticks < MAX_TICKS && !bookwyrm.m_21573_().m_26571_();
    }

    @Override
    public void m_8041_() {
        bookwyrm.m_21573_().m_26573_();
    }
}
