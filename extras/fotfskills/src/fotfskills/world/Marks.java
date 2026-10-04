package fotfskills.world;

import it.unimi.dsi.fastutil.longs.LongOpenHashSet;
import java.util.ArrayList;
import java.util.List;

/** A set of packed block positions (BlockPos.asLong) that can follow blocks a piston moves. */
public final class Marks {
    private final LongOpenHashSet positions = new LongOpenHashSet();

    public boolean mark(long pos) {
        return positions.add(pos);
    }

    public boolean remove(long pos) {
        return positions.remove(pos);
    }

    public boolean contains(long pos) {
        return positions.contains(pos);
    }

    /** from.get(i) moves to to.get(i); only marked blocks carry their mark (cleared first, so chains don't collide). */
    public boolean move(List<Long> from, List<Long> to) {
        List<Long> targets = new ArrayList<>();
        for (int i = 0; i < from.size(); i++) {
            if (positions.remove((long) from.get(i))) {
                targets.add(to.get(i));
            }
        }
        for (long target : targets) {
            positions.add(target);
        }
        return !targets.isEmpty();
    }

    public long[] toArray() {
        return positions.toLongArray();
    }
}
