package fotfskills.compat;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * Puzzle blocks players placed inside a protected structure (a "protect" rule with "reset"), waiting to be cleared so
 * the next player finds the puzzle as it was. Kept in memory: on server stop everything pending is cleared at once, so
 * nothing outlives a restart. Positions are BlockPos.asLong.
 */
public final class PlacedBlocks {
    public record Entry(String dimension, long pos, long due) {}

    private final Map<String, Entry> entries = new LinkedHashMap<>();

    public synchronized void add(String dimension, long pos, long due) {
        entries.put(key(dimension, pos), new Entry(dimension, pos, due));
    }

    public synchronized boolean contains(String dimension, long pos) {
        return entries.containsKey(key(dimension, pos));
    }

    public synchronized void remove(String dimension, long pos) {
        entries.remove(key(dimension, pos));
    }

    /** Removes and returns the entries due at or before now. */
    public synchronized List<Entry> takeDue(long now) {
        List<Entry> out = new ArrayList<>();
        for (Iterator<Entry> it = entries.values().iterator(); it.hasNext(); ) {
            Entry e = it.next();
            if (e.due() <= now) {
                out.add(e);
                it.remove();
            }
        }
        return out;
    }

    public synchronized List<Entry> takeAll() {
        List<Entry> out = new ArrayList<>(entries.values());
        entries.clear();
        return out;
    }

    private static String key(String dimension, long pos) {
        return dimension + "|" + pos;
    }
}
